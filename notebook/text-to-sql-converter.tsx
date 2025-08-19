import React, { useState } from 'react';
import { Database, Play, Copy, RotateCcw, Zap, Code, Trophy } from 'lucide-react';

const AdvancedTextToSQLConverter = () => {
  const [inputText, setInputText] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [complexity, setComplexity] = useState('Medium');

  const hackathonExamples = [
    "Find customers who made purchases in the last 30 days but haven't made any purchases in the current month, with their total lifetime value",
    "Get the top 3 products by sales in each category for the last quarter, including percentage growth from previous quarter",
    "Find employees whose salary is above the department average and who have managed at least 2 direct reports in the last year",
    "Calculate running total of daily sales with 7-day moving average, partitioned by store location",
    "Identify customers with unusual purchasing patterns using z-score analysis on their monthly spending",
    "Find the second highest paid employee in each department along with salary gap from the highest",
    "Get products that are frequently bought together (market basket analysis) with confidence scores above 70%",
    "Calculate customer churn rate by cohort analysis for each signup month in the last 2 years",
    "Find stores where inventory turnover is below average but profit margins are above median",
    "Generate a pivot table showing monthly sales by product category with year-over-year comparison"
  ];

  const advancedSQLPatterns = {
    // Window functions
    windowFunctions: {
      patterns: ['running total', 'moving average', 'rank', 'row number', 'lag', 'lead', 'ntile'],
      generate: (text, table = 'sales') => {
        if (text.includes('running total')) {
          return `SELECT date, amount, SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) as running_total FROM ${table};`;
        }
        if (text.includes('moving average')) {
          const days = text.match(/(\d+)[-\s]?day/)?.[1] || '7';
          return `SELECT date, amount, AVG(amount) OVER (ORDER BY date ROWS ${days-1} PRECEDING) as moving_avg_${days}d FROM ${table};`;
        }
        if (text.includes('rank')) {
          return `SELECT *, RANK() OVER (PARTITION BY category ORDER BY amount DESC) as rank FROM ${table};`;
        }
        return `SELECT *, ROW_NUMBER() OVER (ORDER BY amount DESC) as row_num FROM ${table};`;
      }
    },
    
    // CTEs and subqueries
    ctePatterns: {
      patterns: ['with', 'recursive', 'hierarchical', 'step by step'],
      generate: (text, conditions) => {
        return `WITH monthly_sales AS (
  SELECT DATE_TRUNC('month', date) as month, SUM(amount) as total_sales
  FROM sales 
  WHERE date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY month
),
growth_calc AS (
  SELECT month, total_sales,
    LAG(total_sales) OVER (ORDER BY month) as prev_month_sales,
    (total_sales - LAG(total_sales) OVER (ORDER BY month)) / LAG(total_sales) OVER (ORDER BY month) * 100 as growth_rate
  FROM monthly_sales
)
SELECT * FROM growth_calc WHERE growth_rate > 10;`;
      }
    },

    // Advanced analytics
    analyticsPatterns: {
      patterns: ['cohort', 'churn', 'retention', 'lifetime value', 'z-score', 'percentile'],
      generate: (text) => {
        if (text.includes('cohort')) {
          return `WITH customer_cohorts AS (
  SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) as cohort_month
  FROM orders GROUP BY customer_id
),
cohort_data AS (
  SELECT c.cohort_month, 
    DATE_TRUNC('month', o.order_date) as order_month,
    COUNT(DISTINCT o.customer_id) as customers
  FROM customer_cohorts c
  JOIN orders o ON c.customer_id = o.customer_id
  GROUP BY c.cohort_month, DATE_TRUNC('month', o.order_date)
)
SELECT cohort_month, order_month, customers,
  ROUND(customers * 100.0 / FIRST_VALUE(customers) OVER (PARTITION BY cohort_month ORDER BY order_month), 2) as retention_rate
FROM cohort_data ORDER BY cohort_month, order_month;`;
        }
        if (text.includes('z-score') || text.includes('unusual')) {
          return `WITH customer_stats AS (
  SELECT customer_id, AVG(amount) as avg_purchase, STDDEV(amount) as std_purchase
  FROM orders GROUP BY customer_id
),
z_scores AS (
  SELECT o.customer_id, o.amount,
    (o.amount - cs.avg_purchase) / NULLIF(cs.std_purchase, 0) as z_score
  FROM orders o JOIN customer_stats cs ON o.customer_id = cs.customer_id
)
SELECT customer_id, amount, z_score 
FROM z_scores 
WHERE ABS(z_score) > 2.5 
ORDER BY ABS(z_score) DESC;`;
        }
        return text;
      }
    },

    // Market basket analysis
    basketAnalysis: {
      patterns: ['frequently bought together', 'market basket', 'association rules', 'confidence'],
      generate: () => {
        return `WITH product_pairs AS (
  SELECT a.product_id as product_a, b.product_id as product_b, COUNT(*) as pair_count
  FROM order_items a JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
),
product_counts AS (
  SELECT product_id, COUNT(DISTINCT order_id) as product_count
  FROM order_items GROUP BY product_id
),
total_orders AS (SELECT COUNT(DISTINCT order_id) as total FROM orders)
SELECT pa.product_a, pa.product_b, pa.pair_count,
  ROUND(pa.pair_count * 100.0 / pca.product_count, 2) as confidence_a_to_b,
  ROUND(pa.pair_count * 100.0 / pcb.product_count, 2) as confidence_b_to_a,
  ROUND(pa.pair_count * 100.0 / t.total, 4) as support
FROM product_pairs pa
JOIN product_counts pca ON pa.product_a = pca.product_id
JOIN product_counts pcb ON pa.product_b = pcb.product_id
CROSS JOIN total_orders t
WHERE pa.pair_count >= 10 AND 
  (pa.pair_count * 100.0 / pca.product_count > 70 OR pa.pair_count * 100.0 / pcb.product_count > 70)
ORDER BY support DESC;`;
      }
    },

    // Pivot operations
    pivotPatterns: {
      patterns: ['pivot', 'crosstab', 'transpose'],
      generate: (text) => {
        return `SELECT 
  product_category,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 1 THEN amount END) as Jan,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 2 THEN amount END) as Feb,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 3 THEN amount END) as Mar,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 4 THEN amount END) as Apr,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 5 THEN amount END) as May,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 6 THEN amount END) as Jun,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 7 THEN amount END) as Jul,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 8 THEN amount END) as Aug,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 9 THEN amount END) as Sep,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 10 THEN amount END) as Oct,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 11 THEN amount END) as Nov,
  SUM(CASE WHEN EXTRACT(MONTH FROM date) = 12 THEN amount END) as Dec
FROM sales s JOIN products p ON s.product_id = p.id
WHERE EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY product_category
ORDER BY product_category;`;
      }
    }
  };

  const convertToAdvancedSQL = (text) => {
    const lowerText = text.toLowerCase().trim();
    
    // Check for advanced patterns
    for (const [patternType, config] of Object.entries(advancedSQLPatterns)) {
      for (const pattern of config.patterns) {
        if (lowerText.includes(pattern)) {
          setComplexity('Hard');
          return config.generate(lowerText);
        }
      }
    }

    // Complex query patterns
    if (lowerText.includes('top') && lowerText.includes('each') && lowerText.includes('category')) {
      setComplexity('Hard');
      const num = lowerText.match(/top (\d+)/)?.[1] || '3';
      return `WITH ranked_products AS (
  SELECT p.name, p.category, SUM(s.amount) as total_sales,
    ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(s.amount) DESC) as rank
  FROM products p 
  JOIN sales s ON p.id = s.product_id 
  WHERE s.date >= CURRENT_DATE - INTERVAL '3 months'
  GROUP BY p.id, p.name, p.category
)
SELECT category, name, total_sales, rank
FROM ranked_products 
WHERE rank <= ${num}
ORDER BY category, rank;`;
    }

    if (lowerText.includes('second highest') || lowerText.includes('nth highest')) {
      setComplexity('Hard');
      return `WITH salary_ranks AS (
  SELECT employee_id, name, department, salary,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
  FROM employees
)
SELECT department, name, salary,
  salary - LEAD(salary) OVER (PARTITION BY department ORDER BY salary DESC) as salary_gap
FROM salary_ranks 
WHERE salary_rank = 2;`;
    }

    if (lowerText.includes('haven\'t') || lowerText.includes('but not')) {
      setComplexity('Hard');
      return `SELECT c.customer_id, c.name, SUM(o.amount) as lifetime_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.date >= CURRENT_DATE - INTERVAL '30 days'
  AND c.id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE date >= DATE_TRUNC('month', CURRENT_DATE)
  )
GROUP BY c.customer_id, c.name
ORDER BY lifetime_value DESC;`;
    }

    if (lowerText.includes('above average') || lowerText.includes('above median')) {
      setComplexity('Hard');
      return `WITH dept_stats AS (
  SELECT department, AVG(salary) as avg_salary, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median_salary
  FROM employees GROUP BY department
),
manager_counts AS (
  SELECT manager_id, COUNT(*) as direct_reports
  FROM employees 
  WHERE hire_date >= CURRENT_DATE - INTERVAL '1 year'
  GROUP BY manager_id
)
SELECT e.name, e.department, e.salary, mc.direct_reports
FROM employees e
JOIN dept_stats ds ON e.department = ds.department
LEFT JOIN manager_counts mc ON e.id = mc.manager_id
WHERE e.salary > ds.avg_salary 
  AND COALESCE(mc.direct_reports, 0) >= 2;`;
    }

    if (lowerText.includes('inventory turnover') || lowerText.includes('turnover')) {
      setComplexity('Hard');
      return `WITH inventory_metrics AS (
  SELECT store_id, 
    SUM(cost_of_goods_sold) / AVG(inventory_value) as turnover_ratio,
    (SUM(revenue) - SUM(cost_of_goods_sold)) / SUM(revenue) * 100 as profit_margin
  FROM store_metrics 
  WHERE date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY store_id
),
benchmarks AS (
  SELECT AVG(turnover_ratio) as avg_turnover, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY profit_margin) as median_margin
  FROM inventory_metrics
)
SELECT im.store_id, im.turnover_ratio, im.profit_margin
FROM inventory_metrics im
CROSS JOIN benchmarks b
WHERE im.turnover_ratio < b.avg_turnover AND im.profit_margin > b.median_margin;`;
    }

    // Fallback to basic patterns with medium complexity
    setComplexity('Medium');
    return generateBasicSQL(text);
  };

  const generateBasicSQL = (text) => {
    // Your existing basic SQL generation logic here
    const lowerText = text.toLowerCase().trim();
    let sql = 'SELECT ';
    let tableName = 'customers';
    
    if (lowerText.includes('all') || lowerText.includes('show')) {
      sql += '*';
    } else if (lowerText.includes('count')) {
      sql += 'COUNT(*) as total_count';
    } else {
      sql += '*';
    }
    
    sql += ` FROM ${tableName}`;
    
    if (lowerText.includes('where') || lowerText.includes('from new york')) {
      sql += " WHERE city = 'New York'";
    }
    
    return sql + ';';
  };

  const generateAdvancedMockResult = (text, sqlQuery) => {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('cohort') || lowerText.includes('retention')) {
      return {
        type: 'table',
        headers: ['Cohort Month', 'Order Month', 'Customers', 'Retention Rate %'],
        rows: [
          ['2024-01', '2024-01', '1,247', '100.00'],
          ['2024-01', '2024-02', '892', '71.54'],
          ['2024-01', '2024-03', '654', '52.45'],
          ['2024-02', '2024-02', '1,389', '100.00'],
          ['2024-02', '2024-03', '1,001', '72.07']
        ],
        description: 'Customer retention cohort analysis'
      };
    }

    if (lowerText.includes('z-score') || lowerText.includes('unusual')) {
      return {
        type: 'table',
        headers: ['Customer ID', 'Purchase Amount', 'Z-Score', 'Anomaly Level'],
        rows: [
          ['C00847', '$4,567.89', '3.24', 'High'],
          ['C01293', '$156.23', '-2.87', 'Low'],
          ['C00654', '$3,890.45', '2.91', 'High'],
          ['C01847', '$89.12', '-3.12', 'Very Low']
        ],
        description: 'Customers with unusual purchasing patterns (|z-score| > 2.5)'
      };
    }

    if (lowerText.includes('frequently bought together') || lowerText.includes('market basket')) {
      return {
        type: 'table',
        headers: ['Product A', 'Product B', 'Pair Count', 'Confidence A→B', 'Support %'],
        rows: [
          ['Coffee Maker', 'Coffee Beans', '1,247', '87.3%', '12.4%'],
          ['Laptop', 'Mouse', '2,156', '92.1%', '21.6%'],
          ['Shampoo', 'Conditioner', '3,847', '78.9%', '38.5%'],
          ['Phone', 'Phone Case', '1,892', '95.2%', '18.9%']
        ],
        description: 'Products frequently bought together (confidence > 70%)'
      };
    }

    if (lowerText.includes('top') && lowerText.includes('each category')) {
      return {
        type: 'table',
        headers: ['Category', 'Product', 'Total Sales', 'Rank', 'Growth %'],
        rows: [
          ['Electronics', 'Wireless Headphones', '$2,456,789', '1', '+23.4%'],
          ['Electronics', 'Smart Watch', '$1,892,456', '2', '+18.7%'],
          ['Electronics', 'Tablet', '$1,654,321', '3', '+15.2%'],
          ['Sports', 'Running Shoes', '$987,654', '1', '+31.8%'],
          ['Sports', 'Yoga Mat', '$654,321', '2', '+27.3%'],
          ['Sports', 'Protein Powder', '$543,210', '3', '+19.9%']
        ],
        description: 'Top 3 products by sales in each category (last quarter)'
      };
    }

    if (lowerText.includes('running total') || lowerText.includes('moving average')) {
      return {
        type: 'table',
        headers: ['Date', 'Daily Sales', 'Running Total', '7-Day Moving Avg', 'Store Location'],
        rows: [
          ['2024-08-15', '$45,678', '$2,345,678', '$47,234', 'New York'],
          ['2024-08-16', '$52,345', '$2,398,023', '$48,891', 'New York'],
          ['2024-08-17', '$48,912', '$2,446,935', '$49,234', 'New York'],
          ['2024-08-18', '$54,123', '$2,501,058', '$50,456', 'New York'],
          ['2024-08-19', '$49,876', '$2,550,934', '$51,023', 'New York']
        ],
        description: 'Daily sales with running totals and 7-day moving averages by store'
      };
    }

    // Default advanced result
    return {
      type: 'table',
      headers: ['Metric', 'Value', 'Benchmark', 'Performance'],
      rows: [
        ['Customer LTV', '$2,456', '$2,100', '+16.9%'],
        ['Churn Rate', '2.3%', '3.1%', 'Better'],
        ['Avg Order Value', '$156', '$142', '+9.8%'],
        ['Revenue Growth', '23.4%', '18.0%', '+5.4pp']
      ],
      description: 'Advanced analytics results'
    };
  };

  const handleConvert = () => {
    if (!inputText.trim()) return;
    
    setIsLoading(true);
    setTimeout(() => {
      const result = convertToAdvancedSQL(inputText);
      setSqlQuery(result);
      setQueryResult(generateAdvancedMockResult(inputText, result));
      setIsLoading(false);
    }, 1200);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sqlQuery);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleReset = () => {
    setInputText('');
    setSqlQuery('');
    setQueryResult(null);
    setComplexity('Medium');
  };

  const handleExampleClick = (example) => {
    setInputText(example);
    setSqlQuery('');
    setQueryResult(null);
    setComplexity('Medium');
  };

  const getComplexityColor = () => {
    switch(complexity) {
      case 'Hard': return 'text-red-600 bg-red-100 border-red-300';
      case 'Medium': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      default: return 'text-green-600 bg-green-100 border-green-300';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 min-h-screen">
      <div className="bg-white rounded-lg shadow-xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="relative">
            <Database className="w-10 h-10 text-purple-600" />
            <Trophy className="w-5 h-5 text-yellow-500 absolute -top-1 -right-1" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-2">
              Advanced SQL Converter
              <Zap className="w-6 h-6 text-yellow-500" />
            </h1>
            <p className="text-purple-600 font-medium">Hackathon Edition - Enterprise Level Queries</p>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-4 mb-8">
          <p className="text-gray-700 text-lg leading-relaxed">
            Generate complex, production-ready SQL queries for advanced analytics, window functions, CTEs, cohort analysis, 
            market basket analysis, and more. Perfect for hackathons, data science competitions, and enterprise-level database operations.
          </p>
        </div>

        {/* Hackathon Examples */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Code className="w-6 h-6 text-purple-600" />
            <h3 className="text-xl font-bold text-gray-700">🏆 Hackathon-Level Examples:</h3>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {hackathonExamples.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="text-left p-4 bg-gradient-to-r from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 rounded-lg text-sm text-gray-700 transition-all duration-200 border border-purple-200 hover:border-purple-300 hover:shadow-md"
              >
                <div className="flex items-start gap-2">
                  <span className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    {index + 1}
                  </span>
                  <span>{example}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Input Section */}
        <div className="space-y-6">
          <div>
            <label htmlFor="input-text" className="block text-xl font-bold text-gray-700 mb-3">
              🚀 Describe Your Advanced Query:
            </label>
            <textarea
              id="input-text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="w-full p-6 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none text-lg"
              rows={5}
              placeholder="e.g., Find customers with declining purchase patterns using cohort analysis and predict churn probability with window functions..."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handleConvert}
              disabled={!inputText.trim() || isLoading}
              className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 text-lg font-medium shadow-lg"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Play className="w-6 h-6" />
              )}
              {isLoading ? 'Generating Advanced SQL...' : 'Generate Enterprise SQL'}
            </button>
            
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-6 py-4 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-all duration-200 text-lg font-medium"
            >
              <RotateCcw className="w-6 h-6" />
              Reset
            </button>
          </div>

          {/* SQL Output */}
          {sqlQuery && (
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <label className="block text-xl font-bold text-gray-700">
                    Generated SQL Query:
                  </label>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getComplexityColor()}`}>
                    {complexity} Complexity
                  </span>
                </div>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium"
                >
                  <Copy className="w-5 h-5" />
                  {copied ? 'Copied!' : 'Copy SQL'}
                </button>
              </div>
              
              <div className="relative">
                <pre className="bg-gray-900 text-green-400 p-8 rounded-lg overflow-x-auto font-mono text-sm leading-relaxed max-h-96 overflow-y-auto">
                  <code>{sqlQuery}</code>
                </pre>
              </div>
              
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Enterprise Note:</strong> This query uses advanced SQL features including CTEs, window functions, and complex joins. 
                  Ensure your database supports these features and adjust table/column names to match your schema.
                </p>
              </div>
            </div>
          )}

          {/* Query Results */}
          {queryResult && (
            <div className="mt-8">
              <h3 className="text-xl font-bold text-gray-700 mb-4">📊 Query Results:</h3>
              
              {queryResult.type === 'table' && (
                <div className="bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200 rounded-lg p-6">
                  <div className="mb-4">
                    <p className="text-gray-700 font-medium text-lg">{queryResult.description}</p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border border-gray-300 rounded-lg shadow-sm">
                      <thead className="bg-gradient-to-r from-purple-100 to-blue-100">
                        <tr>
                          {queryResult.headers.map((header, index) => (
                            <th key={index} className="px-6 py-4 text-left text-sm font-bold text-gray-700 border-b">
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.rows.map((row, rowIndex) => (
                          <tr key={rowIndex} className={`${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}>
                            {row.map((cell, cellIndex) => (
                              <td key={cellIndex} className="px-6 py-4 text-sm text-gray-700 border-b">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>🔬 Advanced Analytics:</strong> These results demonstrate complex data patterns and relationships. 
                  In production, these queries would process millions of records using optimized indexes and partitioning strategies.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedTextToSQLConverter;