import pandas as pd
import sqlite3
import mysql.connector
import psycopg2
import re
from typing import Union, Dict, Any, Optional, Tuple
import gradio as gr
import openai
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json
import traceback

# Load environment variables
load_dotenv()

class EnhancedDataAgent:
    """
    Enhanced data agent with OpenAI integration and multiple database support
    """
    
    def __init__(self, 
                 db_config: Dict[str, str] = None, 
                 dataframe: pd.DataFrame = None,
                 openai_api_key: str = None):
        self.db_config = db_config
        self.df = dataframe
        self.engine = None
        self.table_schemas = {}
        
        # Initialize OpenAI
        self.openai_client = None
        if openai_api_key:
            openai.api_key = openai_api_key
            self.openai_client = openai
        elif os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
            
        # Connect to database
        if db_config:
            self._connect_to_database()
            self._load_table_schemas()
    
    def _connect_to_database(self):
        """Connect to various database types"""
        try:
            db_type = self.db_config.get('type', 'sqlite').lower()
            
            if db_type == 'sqlite':
                connection_string = f"sqlite:///{self.db_config['database']}"
            elif db_type == 'mysql':
                connection_string = (
                    f"mysql+pymysql://{self.db_config['user']}:"
                    f"{self.db_config['password']}@{self.db_config['host']}:"
                    f"{self.db_config.get('port', 3306)}/{self.db_config['database']}"
                )
            elif db_type == 'postgresql':
                connection_string = (
                    f"postgresql://{self.db_config['user']}:"
                    f"{self.db_config['password']}@{self.db_config['host']}:"
                    f"{self.db_config.get('port', 5432)}/{self.db_config['database']}"
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
                
            self.engine = create_engine(connection_string)
            return f"✅ Successfully connected to {db_type} database"
            
        except Exception as e:
            error_msg = f"❌ Database connection error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _load_table_schemas(self):
        """Load table schemas for better query generation"""
        try:
            with self.engine.connect() as conn:
                if self.db_config.get('type', 'sqlite').lower() == 'sqlite':
                    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
                else:
                    tables_query = "SHOW TABLES;"
                
                tables_result = conn.execute(text(tables_query))
                tables = [row[0] for row in tables_result]
                
                for table in tables:
                    try:
                        if self.db_config.get('type', 'sqlite').lower() == 'sqlite':
                            schema_query = f"PRAGMA table_info({table});"
                            schema_result = conn.execute(text(schema_query))
                            columns = [row[1] for row in schema_result]
                        else:
                            schema_query = f"DESCRIBE {table};"
                            schema_result = conn.execute(text(schema_query))
                            columns = [row[0] for row in schema_result]
                            
                        self.table_schemas[table] = columns
                    except Exception as e:
                        print(f"Could not load schema for table {table}: {e}")
                        
        except Exception as e:
            print(f"Error loading table schemas: {e}")
    
    def get_schema_info(self) -> str:
        """Get formatted schema information for display"""
        if not self.table_schemas:
            return "No database schema loaded"
        
        schema_info = "📊 **Database Schema:**\n\n"
        for table, columns in self.table_schemas.items():
            schema_info += f"**{table}**: {', '.join(columns)}\n"
        return schema_info
    
    def generate_sql_with_openai(self, natural_query: str) -> str:
        """Use OpenAI to generate SQL queries"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Please provide API key.")
        
        schema_context = "Database Schema:\n"
        for table, columns in self.table_schemas.items():
            schema_context += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"
        
        prompt = f"""
You are a SQL expert. Convert the following natural language query to SQL.

{schema_context}

Natural Language Query: {natural_query}

Requirements:
- Generate valid SQL syntax
- Use appropriate JOINs when needed
- Include proper WHERE clauses for filtering
- Use aggregation functions when appropriate
- Limit results to reasonable numbers (e.g., TOP 100)
- Only return the SQL query, no explanations

SQL Query:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert who converts natural language to SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            return sql_query
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def generate_pandas_with_openai(self, natural_query: str) -> str:
        """Use OpenAI to generate pandas operations"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Please provide API key.")
        
        df_info = ""
        if self.df is not None:
            df_info = f"DataFrame columns: {list(self.df.columns)}\n"
            df_info += f"DataFrame shape: {self.df.shape}\n"
            df_info += f"Column types: {self.df.dtypes.to_dict()}\n"
        
        prompt = f"""
You are a pandas expert. Convert the following natural language query to pandas operations.

{df_info}

Natural Language Query: {natural_query}

Requirements:
- Generate valid pandas syntax
- Use appropriate methods for filtering, grouping, sorting
- The dataframe variable name is 'df'
- Return only the pandas code, no explanations
- Use method chaining when appropriate

Pandas Code:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a pandas expert who converts natural language to pandas operations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            pandas_code = response.choices[0].message.content.strip()
            pandas_code = pandas_code.replace("```python", "").replace("```", "").strip()
            return pandas_code
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        if not self.engine:
            raise ValueError("No database connection available")
        
        try:
            return pd.read_sql_query(sql, self.engine)
        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")
    
    def execute_pandas(self, code: str) -> Union[pd.DataFrame, Any]:
        """Execute pandas code and return results"""
        if self.df is None:
            raise ValueError("No dataframe available")
        
        try:
            local_vars = {'df': self.df, 'pd': pd}
            result = eval(code, {"__builtins__": {}}, local_vars)
            return result
        except Exception as e:
            raise Exception(f"Pandas execution error: {str(e)}")

# Global agent instance
agent = None

def initialize_agent(db_type, openai_key, host="", port="", database="", user="", password="", db_file=""):
    """Initialize the data agent with provided configuration"""
    global agent
    
    try:
        # Create database config
        db_config = None
        if db_type and database:
            if db_type == "sqlite":
                db_config = {'type': 'sqlite', 'database': db_file or database}
            else:
                db_config = {
                    'type': db_type,
                    'host': host,
                    'port': int(port) if port else (3306 if db_type == "mysql" else 5432),
                    'database': database,
                    'user': user,
                    'password': password
                }
        
        # Create sample data as fallback
        sample_data = pd.DataFrame({
            'customer_id': range(1, 101),
            'name': [f'Customer_{i}' for i in range(1, 101)],
            'city': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'] * 25,
            'age': [25, 30, 35, 40, 45] * 20,
            'amount': [100, 200, 300, 400, 500] * 20,
            'order_date': pd.date_range('2024-01-01', periods=100, freq='D')[:100]
        })
        
        agent = EnhancedDataAgent(
            db_config=db_config,
            dataframe=sample_data,
            openai_api_key=openai_key
        )
        
        status_msg = "✅ Agent initialized successfully!"
        if db_config:
            status_msg += f"\n✅ Connected to {db_type} database"
        if openai_key:
            status_msg += "\n✅ OpenAI integration enabled"
        
        schema_info = agent.get_schema_info() if agent.table_schemas else "Using sample data with columns: customer_id, name, city, age, amount, order_date"
        
        return status_msg, schema_info
        
    except Exception as e:
        error_msg = f"❌ Initialization failed: {str(e)}\n{traceback.format_exc()}"
        return error_msg, "No schema available"

def process_natural_query(query, output_type, use_openai):
    """Process natural language query and return results"""
    global agent
    
    if not agent:
        return "❌ Please initialize the agent first", "", ""
    
    if not query.strip():
        return "❌ Please enter a query", "", ""
    
    try:
        result = agent.process_query(query, output_type, use_openai)
        
        if result['success']:
            # Format the results for display
            if isinstance(result['results'], list) and result['results']:
                results_df = pd.DataFrame(result['results'])
                results_display = results_df.to_string(index=False)
            elif hasattr(result['results'], 'to_string'):
                results_display = result['results'].to_string()
            else:
                results_display = str(result['results'])
            
            status = f"✅ Query processed successfully using {result.get('method', 'unknown')} method"
            return status, result['generated_code'], results_display
        else:
            return f"❌ Error: {result['results']}", result.get('generated_code', ''), ""
            
    except Exception as e:
        error_msg = f"❌ Processing error: {str(e)}"
        return error_msg, "", ""

def get_example_query(example_text):
    """Return example query text"""
    return example_text

def upload_csv_file(file):
    """Handle CSV file upload"""
    global agent
    
    if file is None:
        return "No file uploaded", "No data available"
    
    try:
        # Read the CSV file
        df = pd.read_csv(file.name)
        
        # Update agent with new dataframe
        if agent:
            agent.df = df
        else:
            agent = EnhancedDataAgent(dataframe=df, openai_api_key=os.getenv('OPENAI_API_KEY'))
        
        # Return status and data info
        status = f"✅ CSV uploaded successfully! Shape: {df.shape}"
        data_info = f"**Columns**: {', '.join(df.columns)}\n\n**First 5 rows**:\n{df.head().to_string()}"
        
        return status, data_info
        
    except Exception as e:
        return f"❌ Error uploading CSV: {str(e)}", "No data available"

# Create Gradio interface
def create_gradio_interface():
    """Create and return Gradio interface"""
    
    with gr.Blocks(title="🚀 Enhanced Data Query Agent", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🚀 Enhanced Natural Language Data Agent
        Convert your English questions into SQL queries or pandas operations using AI
        """)
        
        with gr.Tab("🔧 Configuration"):
            gr.Markdown("### Setup your database connection and OpenAI integration")
            
            with gr.Row():
                with gr.Column():
                    openai_key = gr.Textbox(
                        label="OpenAI API Key",
                        placeholder="sk-...",
                        type="password",
                        value=os.getenv('OPENAI_API_KEY', '')
                    )
                    
                    db_type = gr.Dropdown(
                        choices=["sqlite", "mysql", "postgresql"],
                        label="Database Type",
                        value="sqlite"
                    )
                    
                with gr.Column():
                    with gr.Group():
                        gr.Markdown("**Database Connection Details**")
                        host = gr.Textbox(label="Host", placeholder="localhost")
                        port = gr.Textbox(label="Port", placeholder="3306 for MySQL, 5432 for PostgreSQL")
                        database = gr.Textbox(label="Database Name", placeholder="your_database")
                        user = gr.Textbox(label="Username")
                        password = gr.Textbox(label="Password", type="password")
                        db_file = gr.Textbox(label="SQLite File Path", placeholder="data.db")
            
            with gr.Row():
                init_btn = gr.Button("Initialize Agent", variant="primary", size="lg")
                
            with gr.Row():
                status_output = gr.Textbox(label="Status", interactive=False)
                schema_output = gr.Markdown(label="Database Schema")
            
            # CSV Upload Section
            gr.Markdown("### 📁 Or Upload CSV File")
            with gr.Row():
                csv_file = gr.File(label="Upload CSV", file_types=[".csv"])
                csv_status = gr.Textbox(label="Upload Status", interactive=False)
            csv_data_info = gr.Markdown(label="Data Information")
        
        with gr.Tab("💬 Query Interface"):
            gr.Markdown("### Ask questions about your data in plain English")
            
            with gr.Row():
                with gr.Column(scale=3):
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="e.g., Show me the top 10 customers by revenue",
                        lines=3
                    )
                    
                with gr.Column(scale=1):
                    output_type = gr.Radio(
                        choices=["sql", "pandas"],
                        label="Output Type",
                        value="sql"
                    )
                    use_openai = gr.Checkbox(
                        label="Use OpenAI",
                        value=True
                    )
                    
            process_btn = gr.Button("Generate Query", variant="primary", size="lg")
            
            with gr.Row():
                query_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                with gr.Column():
                    generated_code = gr.Code(label="Generated Code", language="sql")
                with gr.Column():
                    results_output = gr.Textbox(label="Results", lines=10, max_lines=20)
        
        with gr.Tab("📚 Examples"):
            gr.Markdown("### Click on any example to try it out")
            
            examples = [
                "Count customers by city",
                "Show customers older than 30",
                "Calculate average age of customers",
                "Find top 5 customers by amount",
                "Show me monthly trends in customer orders",
                "Which city has the highest average order value?",
                "Find customers who made orders in the last 30 days",
                "Calculate total revenue by month"
            ]
            
            with gr.Row():
                for i, example in enumerate(examples):
                    if i % 4 == 0 and i > 0:
                        gr.HTML("<br>")
                    example_btn = gr.Button(example, size="sm")
                    example_btn.click(
                        fn=lambda x=example: x,
                        outputs=query_input
                    )
        
        # Event handlers
        init_btn.click(
            fn=initialize_agent,
            inputs=[db_type, openai_key, host, port, database, user, password, db_file],
            outputs=[status_output, schema_output]
        )
        
        csv_file.upload(
            fn=upload_csv_file,
            inputs=[csv_file],
            outputs=[csv_status, csv_data_info]
        )
        
        process_btn.click(
            fn=process_natural_query,
            inputs=[query_input, output_type, use_openai],
            outputs=[query_status, generated_code, results_output]
        )
        
        # Add some example queries that auto-fill
        gr.Examples(
            examples=[
                ["Count customers by city", "sql", True],
                ["Show top 10 customers by amount", "sql", True],
                ["Calculate average age", "pandas", True],
                ["Filter customers older than 35", "pandas", True],
            ],
            inputs=[query_input, output_type, use_openai],
        )
    
    return demo

# Main execution
if __name__ == "__main__":
    # Create and launch the interface
    demo = create_gradio_interface()
    
    # Launch with different options
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=True,            # Create public link
        debug=True             # Enable debug mode
    )