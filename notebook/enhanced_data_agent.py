import pandas as pd
import sqlite3
import re
from typing import Union, Dict, Any, List
import streamlit as st
import openai
import os
from datetime import datetime
import json

class EnhancedDataAgent:
    """
    Enhanced data agent with OpenAI integration for better natural language understanding
    """
    
    def __init__(self, db_path: str = None, dataframe: pd.DataFrame = None, openai_api_key: str = None):
        self.db_path = db_path
        self.df = dataframe
        self.conn = None
        self.openai_client = None
        self.table_schema = {}
        
        # Initialize database connection
        if db_path:
            self.conn = sqlite3.connect(db_path)
            self._load_table_schema()
            
        # Initialize OpenAI client
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        elif os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def _load_table_schema(self):
        """Load database schema information"""
        if not self.conn:
            return
            
        cursor = self.conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            self.table_schema[table_name] = {
                'columns': [col[1] for col in columns],  # column names
                'types': [col[2] for col in columns],    # column types
                'schema_info': columns
            }
    
    def get_schema_context(self) -> str:
        """Generate schema context for OpenAI"""
        if not self.table_schema:
            if self.df is not None:
                return f"DataFrame columns: {list(self.df.columns)}\nData types: {self.df.dtypes.to_dict()}"
            return "No schema information available"
        
        schema_text = "Database Schema:\n"
        for table_name, info in self.table_schema.items():
            schema_text += f"\nTable: {table_name}\n"
            for col, dtype in zip(info['columns'], info['types']):
                schema_text += f"  - {col} ({dtype})\n"
        
        return schema_text
    
    def openai_to_sql(self, query: str) -> str:
        """Use OpenAI to convert natural language to SQL"""
        if not self.openai_client:
            return self.fallback_sql_generation(query)
        
        schema_context = self.get_schema_context()
        
        prompt = f"""
Given the following database schema:
{schema_context}

Convert this natural language query to SQL:
"{query}"

Requirements:
- Generate only valid SQL code
- Use proper table and column names from the schema
- Include appropriate WHERE, GROUP BY, ORDER BY clauses as needed
- Return only the SQL query without explanations
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only valid SQL queries based on the schema provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Clean up the response (remove markdown formatting if present)
            sql_query = re.sub(r'```sql\n?', '', sql_query)
            sql_query = re.sub(r'```\n?', '', sql_query)
            
            return sql_query
            
        except Exception as e:
            st.error(f"OpenAI API error: {str(e)}")
            return self.fallback_sql_generation(query)
    
    def openai_to_pandas(self, query: str) -> str:
        """Use OpenAI to convert natural language to pandas operations"""
        if not self.openai_client:
            return self.fallback_pandas_generation(query)
        
        column_info = ""
        if self.df is not None:
            column_info = f"DataFrame columns: {list(self.df.columns)}\nSample data:\n{self.df.head().to_string()}"
        
        prompt = f"""
Given this pandas DataFrame:
{column_info}

Convert this natural language query to pandas code:
"{query}"

Requirements:
- Generate only valid pandas code that works with df
- Use proper column names from the DataFrame
- Return only the pandas expression without explanations
- Assume the DataFrame variable is named 'df'
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a pandas expert. Generate only valid pandas code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            pandas_code = response.choices[0].message.content.strip()
            # Clean up the response
            pandas_code = re.sub(r'```python\n?', '', pandas_code)
            pandas_code = re.sub(r'```\n?', '', pandas_code)
            
            return pandas_code
            
        except Exception as e:
            st.error(f"OpenAI API error: {str(e)}")
            return self.fallback_pandas_generation(query)
    
    def fallback_sql_generation(self, query: str) -> str:
        """Fallback SQL generation when OpenAI is not available"""
        query_lower = query.lower()
        
        # Use the original pattern matching logic
        patterns = {
            'count_by_group': {
                'keywords': ['count', 'group', 'by'],
                'sql': "SELECT {column}, COUNT(*) as count FROM {table} GROUP BY {column} ORDER BY count DESC;"
            },
            'total_sum': {
                'keywords': ['total', 'sum'],
                'sql': "SELECT SUM({column}) as total FROM {table};"
            },
            'average': {
                'keywords': ['average', 'avg', 'mean'],
                'sql': "SELECT AVG({column}) as average FROM {table};"
            },
            'filter': {
                'keywords': ['where', 'filter'],
                'sql': "SELECT * FROM {table} WHERE {column} = '{value}';"
            }
        }
        
        # Try to match patterns and generate SQL
        for pattern_name, pattern_data in patterns.items():
            if any(keyword in query_lower for keyword in pattern_data['keywords']):
                sql = pattern_data['sql']
                
                # Try to infer table and column names
                table_name = list(self.table_schema.keys())[0] if self.table_schema else 'customers'
                column = self._extract_column(query_lower)
                
                sql = sql.format(table=table_name, column=column, value='value')
                return sql
        
        # Generic fallback
        table_name = list(self.table_schema.keys())[0] if self.table_schema else 'customers'
        return f"SELECT * FROM {table_name} LIMIT 10;"
    
    def fallback_pandas_generation(self, query: str) -> str:
        """Fallback pandas generation when OpenAI is not available"""
        # Use the original pandas logic
        query_lower = query.lower()
        
        if 'group' in query_lower:
            column = self._extract_column(query_lower)
            return f"df.groupby('{column}').size().sort_values(ascending=False)"
        
        if 'filter' in query_lower:
            column = self._extract_column(query_lower)
            return f"df[df['{column}'].notna()]"
        
        if any(word in query_lower for word in ['average', 'mean']):
            column = self._extract_column(query_lower)
            return f"df['{column}'].mean()"
        
        return "df.head(10)"
    
    def connect_to_database(self, db_path: str):
        """Connect to a new database"""
        try:
            if self.conn:
                self.conn.close()
            
            self.db_path = db_path
            self.conn = sqlite3.connect(db_path)
            self._load_table_schema()
            return True
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return False
    
    def load_csv_to_database(self, csv_path: str, table_name: str):
        """Load CSV file into SQLite database"""
        try:
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            self._load_table_schema()  # Refresh schema
            return True
        except Exception as e:
            st.error(f"CSV loading error: {str(e)}")
            return False
    
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        if not self.conn:
            raise ValueError("No database connection available")
        
        try:
            return pd.read_sql_query(sql, self.conn)
        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")
    
    def execute_pandas(self, code: str) -> Union[pd.DataFrame, Any]:
        """Execute pandas code and return results"""
        if self.df is None:
            raise ValueError("No dataframe available")
        
        try:
            # Create safe execution environment
            local_vars = {'df': self.df, 'pd': pd}
            result = eval(code, {"__builtins__": {}}, local_vars)
            return result
        except Exception as e:
            raise Exception(f"Pandas execution error: {str(e)}")
    
    def process_query(self, natural_query: str, output_type: str = 'sql') -> Dict[str, Any]:
        """Process natural language query and return results"""
        try:
            if output_type == 'sql':
                generated_code = self.openai_to_sql(natural_query)
                if self.conn:
                    results = self.execute_sql(generated_code)
                    return {
                        'query': natural_query,
                        'generated_code': generated_code,
                        'results': results.to_dict('records') if not results.empty else [],
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'query': natural_query,
                        'generated_code': generated_code,
                        'results': 'No database connected - code generated only',
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
            else:  # pandas
                generated_code = self.openai_to_pandas(natural_query)
                if self.df is not None:
                    results = self.execute_pandas(generated_code)
                    return {
                        'query': natural_query,
                        'generated_code': generated_code,
                        'results': results if not hasattr(results, 'to_dict') else results.to_dict('records'),
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'query': natural_query,
                        'generated_code': generated_code,
                        'results': 'No dataframe loaded - code generated only',
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                'query': natural_query,
                'generated_code': '',
                'results': f'Error: {str(e)}',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
    
    # Helper methods
    def _extract_number(self, query: str) -> int:
        match = re.search(r'\d+', query)
        return int(match.group()) if match else None
    
    def _extract_column(self, query: str) -> str:
        # Try to find column names from schema
        if self.table_schema:
            for table_info in self.table_schema.values():
                for col in table_info['columns']:
                    if col.lower() in query.lower():
                        return col
        
        # Fallback to common column names
        if self.df is not None:
            for col in self.df.columns:
                if col.lower() in query.lower():
                    return col
        
        # Default fallback
        columns = ['name', 'age', 'amount', 'city', 'email', 'date']
        for col in columns:
            if col in query.lower():
                return col
        return 'id'
    
    def _extract_keyword(self, query: str) -> str:
        words = query.split()
        stop_words = {'the', 'and', 'with', 'from', 'where', 'select', 'show', 'get', 'find'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[0] if keywords else 'search'

def main():
    st.set_page_config(page_title="Enhanced Data Query Agent", layout="wide")
    
    st.title("🤖 Enhanced Natural Language Data Agent")
    st.markdown("Convert your English questions into SQL queries or pandas operations using OpenAI")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # OpenAI API Key input
        openai_key = st.text_input("OpenAI API Key", type="password", 
                                  help="Enter your OpenAI API key for enhanced query understanding")
        
        # Database connection options
        st.subheader("Data Source")
        data_option = st.radio("Choose data source:", 
                             ["Upload CSV", "Connect to Database", "Use Sample Data"])
        
        if data_option == "Upload CSV":
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.session_state.agent = EnhancedDataAgent(dataframe=df, openai_api_key=openai_key)
                st.success(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
                st.write("Columns:", list(df.columns))
        
        elif data_option == "Connect to Database":
            db_path = st.text_input("Database Path", 
                                   placeholder="path/to/your/database.db")
            if db_path and st.button("Connect"):
                agent = EnhancedDataAgent(openai_api_key=openai_key)
                if agent.connect_to_database(db_path):
                    st.session_state.agent = agent
                    st.success("Connected to database!")
                    # Display schema
                    if agent.table_schema:
                        st.write("Tables found:")
                        for table, info in agent.table_schema.items():
                            st.write(f"- {table}: {', '.join(info['columns'])}")
        
        else:  # Sample data
            sample_data = pd.DataFrame({
                'employee_id': range(1, 101),
                'name': [f'Employee_{i}' for i in range(1, 101)],
                'department': ['Sales', 'Engineering', 'Marketing', 'HR'] * 25,
                'city': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'] * 25,
                'age': [25 + (i % 15) for i in range(100)],
                'salary': [50000 + (i * 1000) for i in range(100)],
                'hire_date': pd.date_range('2020-01-01', periods=100, freq='W')
            })
            st.session_state.agent = EnhancedDataAgent(dataframe=sample_data, openai_api_key=openai_key)
            st.success("Using sample employee data")
    
    # Main interface
    if 'agent' not in st.session_state:
        st.info("Please configure your data source in the sidebar to get started.")
        return
    
    agent = st.session_state.agent
    
    # Query input section
    st.subheader("Ask Your Question")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "Ask your question in plain English:",
            placeholder="e.g., Show me the top 10 employees by salary in the Engineering department",
            height=100,
            key="user_query"
        )
    
    with col2:
        output_type = st.selectbox("Output Type:", ["sql", "pandas"])
        use_openai = st.checkbox("Use OpenAI (Enhanced)", value=bool(openai_key))
        
        if st.button("Generate Query", type="primary"):
            if query:
                with st.spinner("Processing your query..."):
                    # Choose method based on user preference
                    if use_openai and agent.openai_client:
                        result = agent.process_query(query, output_type)
                    else:
                        # Use fallback method
                        if output_type == 'sql':
                            generated_code = agent.fallback_sql_generation(query)
                        else:
                            generated_code = agent.fallback_pandas_generation(query)
                        
                        result = {
                            'query': query,
                            'generated_code': generated_code,
                            'results': 'Code generated (execute to see results)',
                            'success': True,
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    st.session_state.last_result = result
    
    # Display results
    if 'last_result' in st.session_state:
        result = st.session_state.last_result
        
        st.subheader("Generated Code")
        st.code(result['generated_code'], language=output_type if output_type == 'sql' else 'python')
        
        # Copy button for generated code
        st.button("📋 Copy Code", key="copy_code")
        
        # Execute button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("▶️ Execute", type="secondary"):
                try:
                    if output_type == 'sql':
                        if agent.conn:
                            exec_result = agent.execute_sql(result['generated_code'])
                            st.session_state.execution_result = exec_result
                        else:
                            st.error("No database connection available")
                    else:
                        if agent.df is not None:
                            exec_result = agent.execute_pandas(result['generated_code'])
                            st.session_state.execution_result = exec_result
                        else:
                            st.error("No dataframe available")
                except Exception as e:
                    st.error(f"Execution error: {str(e)}")
        
        # Display execution results
        if 'execution_result' in st.session_state:
            st.subheader("Query Results")
            exec_result = st.session_state.execution_result
            
            if isinstance(exec_result, pd.DataFrame):
                st.dataframe(exec_result, use_container_width=True)
                st.caption(f"Showing {len(exec_result)} rows")
            else:
                st.write(exec_result)
    
    # Query History
    if st.checkbox("Show Query History"):
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        if 'last_result' in st.session_state:
            # Add to history
            result = st.session_state.last_result
            if result not in st.session_state.query_history:
                st.session_state.query_history.append(result)
        
        if st.session_state.query_history:
            st.subheader("Previous Queries")
            for i, hist_result in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history)-i}: {hist_result['query'][:50]}..."):
                    st.code(hist_result['generated_code'])
                    st.caption(f"Generated at: {hist_result['timestamp']}")
    
    # Example queries section
    st.subheader("Example Queries")
    
    if agent.table_schema:
        # Generate examples based on actual schema
        table_names = list(agent.table_schema.keys())
        examples = [
            f"Show me all records from {table_names[0]}",
            f"Count records by department in {table_names[0]}",
            f"Find the average salary in {table_names[0]}",
            f"Show top 10 highest paid employees"
        ]
    else:
        examples = [
            "Show me all employees from Engineering department",
            "Count employees by city",
            "Calculate average salary",
            "Find top 5 employees by salary",
            "Show employees hired in 2023",
            "Get unique departments"
        ]
    
    cols = st.columns(3)
    for i, example in enumerate(examples[:6]):
        with cols[i % 3]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.user_query = example
                st.rerun()
    
    # Database schema display
    if agent.table_schema:
        with st.expander("View Database Schema"):
            for table_name, info in agent.table_schema.items():
                st.write(f"**Table: {table_name}**")
                schema_df = pd.DataFrame({
                    'Column': info['columns'],
                    'Type': info['types']
                })
                st.dataframe(schema_df, use_container_width=True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # CLI mode
        query = " ".join(sys.argv[1:])
        
        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        
        agent = EnhancedDataAgent(openai_api_key=openai_key)
        result = agent.process_query(query, 'sql')
        
        print(f"Query: {result['query']}")
        print(f"Generated Code:\n{result['generated_code']}")
        if result['success']:
            print(f"Results: {result['results']}")
        else:
            print(f"Error: {result['results']}")
    else:
        # Streamlit mode
        main()