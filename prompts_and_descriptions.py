# Prompt for generating descriptions of CSV files in a folder
folder_csv_description_prompt = """
You are a data assistant. Your task is to analyze multiple CSV files in a given folder. 
First, list all CSV files present in the folder. Then, generate a structured JSON description for each file based on its column names.

### **Input:**
- A folder containing multiple CSV files.

### **Output:**
A structured JSON object with details about each CSV file.

### **Example:**

#### **Input:**
Folder contains:
1. `ecom/customers.csv` (Columns: ["customer_id", "customer_name", "customer_email", "purchase_date"])
2. `ecom/second_ecom/sales.csv` (Columns: ["order_id", "product_id", "price", "order_date", "quantity"])
3. `inventory.csv` (Columns: ["product_id", "product_name", "stock_quantity", "reorder_level"])

#### **Output:**
{{
    "CSV FILES": [
        {{
            "File Name": "ecom/customers.csv",
            "File Description": "This file contains customer details and their purchase records.",
            "Key Columns": [
                {{"Column Name": "customer_id", "Description": "Unique identifier for each customer."}},
                {{"Column Name": "customer_name", "Description": "Full name of the customer."}},
                {{"Column Name": "customer_email", "Description": "Email address of the customer."}},
                {{"Column Name": "purchase_date", "Description": "Date when the customer made a purchase."}}
            ]
        }},
        {{
            "File Name": "ecom/second_ecom/sales.csv",
            "File Description": "This file contains sales transactions including order details and pricing.",
            "Key Columns": [
                {{"Column Name": "order_id", "Description": "Unique identifier for each order."}},
                {{"Column Name": "product_id", "Description": "ID of the product sold."}},
                {{"Column Name": "price", "Description": "Price of the product."}},
                {{"Column Name": "order_date", "Description": "Date when the order was placed."}},
                {{"Column Name": "quantity", "Description": "Number of units sold in the order."}}
            ]
        }},
        {{
            "File Name": "inventory.csv",
            "File Description": "This file contains inventory stock details including available stock and reorder levels.",
            "Key Columns": [
                {{"Column Name": "product_id", "Description": "Unique identifier for each product."}},
                {{"Column Name": "product_name", "Description": "Name of the product."}},
                {{"Column Name": "stock_quantity", "Description": "Current stock available."}},
                {{"Column Name": "reorder_level", "Description": "Stock level at which reorder is needed."}}
            ]
        }}
    ]
}}

Now, analyze and generate descriptions for all CSV files : {csv_info}

    return a properly formatted JSON object.
    Do NOT include any extra text or explanations, and their full File Name in the output json 
    Follow this format:
    {{
        "CSV FILES":   {{
            "File Name": "ecom/customers.csv",
            "File Description": "This file contains customer details and their purchase records.",
            "Key Columns": [
                {{"Column Name": "customer_id", "Description": "Unique identifier for each customer."}},
                {{"Column Name": "customer_name", "Description": "Full name of the customer."}},
                {{"Column Name": "customer_email", "Description": "Email address of the customer."}},
                {{"Column Name": "purchase_date", "Description": "Date when the customer made a purchase."}}
            ]
        }}
    }}
"""



# if need to predict the description for csv files from llm


# csv_files = []
# for dirname, _, filenames in os.walk('ecom/second_ecom/'):
#     for filename in filenames:
#         full_path = os.path.join(dirname, filename)
#         csv_files.append(full_path)
#         df =  pd.read_csv(full_path,nrows=1)


# csv_data = {}

# for file in csv_files:
#     # file_path = os.path.join('ecom', file)
#     filename = file.split('/')[-1].split('.')[0]
#     try:
#         df = pd.read_csv(file, nrows=1)  
#         csv_data[file] = list(df.columns)
#     except Exception as e:
#         print(f"Error reading {file}: {e}")

# csv_info = [{"File Name": file, "Columns": columns} for file, columns in csv_data.items()]


# folder_csv_description_prompt
# prompt = folder_csv_description_prompt.format(csv_info=csv_info)
# prediction = llm.predict(prompt)


# response_schemas = [
#     ResponseSchema(name="CSV FILES", description="The Hive SQL query")
# ]

# parser = StructuredOutputParser.from_response_schemas(response_schemas)
# csv_json = parser.parse(prediction)




query_generation_template = """You are an AI assistant responsible for generating correct Pandas queries based on CSV metadata.

        ## **Instructions**
        - You **must** reference CSV files **only** by their **full file path** from `File Name` in `{csv_info}`.
        - **Never use short file names** (e.g., `"customers.csv"`). Always use the full path 
        Example File Name to use in read_csv method: 
        File Name = "ecom/second_ecom/customers.csv"
        - Ensure **division operations** avoid `ZeroDivisionError`.  
        - Save the resulting DataFrame as a CSV file in the current directory.
        - **Return only** the query in JSON format, with **no additional text**.
        - Always ensure the query is efficient and uses appropriate filtering, merging and sorting techniques. 
        - **If Possible use merge in last after applying filtering.**
        - **And If Possible do not use merge if not required.**
        - Do Not apply joins on the full tables unnecessarily.
        - If Same data is present in multiple files then use all file and makes aggregated results on all files but keep in mind that all records should be different in all files.
        - Safely computes argmax on a sequence, ensuring error handling for empty data.
        - If the data is empty after any filtering or any operations, stores empty DataFrame with column names.
        - If user's questions did not use case sensitive words like equals to , exact match , contains for comparing then convert both strings (noun in question and dataframe column)to lower case and then compare.
        - else use the relevant methods or fuctions asks in the question.
        - Filtering should be more case sensitive if users questions specify the keywords like contains, exact,equals to,exactly etc,then use methods for case sensitivity maintains the original text from the question.  
        - Handles ValueError and other exceptions gracefully.

        examples to take refrence for the final output 
        Examples :
          city_sales = df_last_6_months.groupby('city_name')['total_discount_amount'].sum().reset_index(); 
          result = city_sales.loc[city_sales['total_discount_amount'].idxmax()]
          
          here you are using idxmax function which is causing the error because there no data available in city sales dataframe so handles it accordingly either use try and except or use if and else condtions
            sample code you can create :
            if not city_sales.empty: 
                result = city_sales.loc[city_sales['total_discount_amount'].idxmax()]; 
            else: 
                result = pd.DataFrame(columns=['city_name', 'total_discount_amount']); 
            result.to_csv('output.csv', index=False)

        Also maintains the indentations and syntax errors are handled.
        
        "You are a coding assistant. Generate Python code carefully, ensuring that:\n"
        " The code is syntactically correct.and it has proper indentations and all for if and else or looping conditions.\n"
        " It does not contain missing colons or indentation errors.\n"
        " All variables and functions are properly defined before use.\n"
        " If any syntax error is detected, fix it before returning the response."
        ---
        User question : give total sales of product name contains exactly ONioN
        expected output:
        {{
        
        "Pandas Query": "\nimport pandas as pd\ndf = pd.read_csv('ecom/second_ecom/xyz.csv')\ndf_filtered = df[df['product_name'].str.contains('ONioN', case=True)]\ntotal_sales = df_filtered['total_weighted_landing_price'].sum()\nresult = pd.DataFrame({{'total_sales': [total_sales]}})\nif result.empty:\n    result = pd.DataFrame(columns=['total_sales'])\nresult.to_csv('output_second.csv', index=False)\n"
        
        }}

        here we use exactly keyword that's why we takes ONIoN as it is from question.

        ## **Example Input:**
        _User Question_: "Get all customers who made a purchase after 2023-01-01."

        ---
        **save the output in the output_second.csv file**
        ## **Example Output (JSON)**
        ```json
        {{
            "Pandas Query": "\nimport pandas as pd\ndf = pd.read_csv('ecom/second_ecom/wrfewgrg3g313.csv')\ndf['date_'] = pd.to_datetime(df['date_'])\ndf['year'] = df['date_'].dt.year\nresult = df.groupby('year')['product_id'].count().reset_index()\nresult.columns = ['year', 'number_of_orders']\nif result.empty:\n    result = pd.DataFrame(columns=['year', 'number_of_orders'])\nresult.to_csv('output_second.csv', index=False)\n"      
              
        }}

            Below is the metadata of all available CSV files. Always refer to them using the File Name.

        

            {csv_info}.

          User Question: {input}"""




predicting_plots_template="""
    Given the following details of the DataFrame, determine the best visual plot names like 
    [stack bar graph, bar and line, count, bar, line, pie, kde, etc.] and the variables to plot against.
    
    - Column names are provided in a list format.
    - You must also suggest one dynamic plot.
    - You can give multiple columns if the graph is appropriate.
    - Provide column names only from the DataFrame.
    - If providing a single column, choose a count plot.
    - Prefer numerical columns and multiple columns for better visual appeal.
    - For a pie chart, provide at least two variables.
    - If the question already contains a plot name, recommend that.
    
    **DataFrame Information:**
    - **Columns:** {column_name}
    - **Column Datatypes:** {column_data_dtype}
    - **Number of Rows:** {length_df}

    Please provide the response in JSON format:

    ```json
    {{
        "Plot Name": "<plot_type>",
        "Variables": ["<column1>", "<column2>"]
    }}
    ```
    """



graph_generation_template="""    

    Do not create sample data or sample dataframes.
    Do not add any extra lines in the output just return the python code.No text like : here is the python code and similar to like that,Or Just comment those lines.
    Use the columns provided below without making assumptions about them.
    Assume df is the dataframe containing the data.
    Dont use plt.figure(figsize=())
    Generate Python code using either [matplotlib, seaborn] for the specified graph: {plot_name}.
    Use the columns provided in the dataframe: {variables}.
    Use plt.tight_layout().
    If the length of df exceeds 100, use df=df.head(100).
    For pie charts, write code to avoid the ValueError: Wedge sizes 'x' must be non-negative values, and ensure the labels length matches.
    Rotate the x-axis labels by either 45 or 90 degrees.
    Example:

    #Ex5: Pie chart
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)


    #Ex4: Countplot
        sns.countplot(x ='figure', data = df)


    #Ex 1: bar plot 
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        sns.barplot(x='month', y='order_count', data=df, palette='viridis')
        plt.title('Monthly Order Count')
        plt.xlabel('Month')
        plt.ylabel('Number of Orders')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.xticks(rotation=90)
        plt.legend()
        plt.tight_layout()


    #Ex 2: bar and line plot
        fig, ax1 = plt.subplots()
        # Bar plot (left y-axis)
        ax1.bar(categories, bar_data, color='darkblue', width=0.6, label='Bar Data')
        ax1.set_ylabel('Bar Data', color='darkblue')

        # Line plot (right y-axis)
        ax2 = ax1.twinx()
        ax2.plot(categories, line_data, color='orange', marker='o', linestyle='-', linewidth=2, label='Line Data')
        ax2.set_ylabel('Line Data', color='orange')
        # Title and legend
        plt.title('Bar and Line Graph')
        plt.tight_layout()
        fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), shadow=True, ncol=2)
        # Show plot
        plt. margins(x=0)

    #Ex3 : Stacked bar chart
        df['Date'] = pd.to_datetime(df['Date'], format='%B %Y')
        # Stacked bar plot
        plt.bar(df['Date'], df['ALL'], color='blue', label='ALL')
        plt.bar(df['Date'], df['Incomplete'], bottom=df['ALL'], color='red', label='Incomplete')
        plt.bar(df['Date'], df['Unlisted'], bottom=df['ALL'] + df['Incomplete'], color='orange', label='Unlisted')
        plt.bar(df['Date'], df['Doctor Locator - Listed'], bottom=df['ALL'] + df['Incomplete'] + df['Unlisted'], color='green', label='Doctor Locator - Listed')

        # Adding title and labels
        plt.title('Total Potential vs Listed')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.legend()

        # Display the plot
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt. margins(x=0)

    Additional functionalities:
        1. Add titles and axis labels to the plots.
        2. Customize colors to enhance visual appeal.
        3. Add legends to the plots where applicable.
        4. For line plots, include markers for data points.
        5. Add grid lines to the plots for better readability.
        6. For bar plots, include the values on top of the bars.
        7. For scatter plots, include a trendline if applicable.
        8. Handle missing data gracefully by ignoring or filling with appropriate values.
        9. Ensure the code is well-commented and modular.
        10. Include error handling to manage unexpected issues gracefully.
        11. Bar graph bar width to be 0.3 and use a single color

    Make the graph colorful and visually appealing by:
    - Adding appropriate titles, axis labels, and legends.
    - Using different colors for different categories.
    - Adding gridlines for better readability.
    - Including trend lines or error bars where applicable.
    - Rotating the x-axis labels for better visibility if needed.
    - Employing different styles for markers and lines to distinguish data points.
    - Adjusting figure size and layout to make it clear and legible.
    - Annotating data points where necessary to highlight key information.
    - Using custom fonts and styles to enhance aesthetics.
    - Incorporating a background color or theme for better visual impact.
    - Ensuring axis scales and intervals are appropriate for the data range.
    - Adding interactivity (e.g., tooltips) if using a library that supports it.
    
    Ensure the graph is informative and well-presented."""




# Meta Data for csv file which contains descriptions of Columns.
csv_json = {
    "CSV_FILES": [
        {
        "File Name": "ecom/second_ecom/xyz.csv",
        "File Description": "This file contains product details and order details.",
        "Key Columns": [
            {"Column Name": "date_","Description": "Date of the order."}, 
            {"Column Name": "city_name","Description": "City where the order occurred."}, 
            {"Column Name": "order_id","Description": "Unique identifier for each order."}, 
            {"Column Name": "cart_id","Description": "ID of the shopping cart."}, 
            {"Column Name": "dim_customer_key","Description": "Customer identifier."}, 
            {"Column Name": "procured_quantity","Description": "Number of products."}, 
            {"Column Name": "unit_selling_price","Description": "Price of the product per unit."}, 
            {"Column Name": "total_discount_amount","Description": "Total discount provided on the order."}, 
            {"Column Name": "product_id","Description": "Unique identifier for each product."}, 
            {"Column Name": "total_weighted_landing_price","Description": "Total sales price of the products, after all discounts."}, 
            {"Column Name": "product_name","Description": "Name of the product."}, 
            {"Column Name": "unit","Description": "Unit of the product."}, 
            {"Column Name": "product_type","Description": "Type of the product."}, 
            {"Column Name": "brand_name","Description": "Name of the product's brand."}, 
            {"Column Name": "manufacturer_name","Description": "Name of the product's manufacturer."}, 
            {"Column Name": "l0_category","Description": "Category level zero of the sales table."}, 
            {"Column Name": "l1_category","Description": "Category level one of the order of sales table."}, 
            {"Column Name": "l2_category","Description": "Category level two of the order.of sales table."}, 
            {"Column Name": "l0_category_id","Description": "ID of the category level zero of the product."}, 
            {"Column Name": "l1_category_id","Description": "ID of the category level one of the product."}, 
            {"Column Name": "l2_category_id","Description": "ID of the category level two of the product."}, 
            {"Column Name": "Unnamed: 0","Description": "Row identifier."}, 
            {"Column Name": "Unnamed: 0.2","Description": "Unknown purpose."}, 
            {"Column Name": "Unnamed: 0.1","Description": "Unknown purpose."}, 
            {"Column Name": "Unnamed: 0_x","Description": "Unknown purpose."}, 
            {"Column Name": "Unnamed: 0_y","Description": "Unknown purpose."}
            ]
        },  
          
            {
            "File Name": "ecom/second_ecom/cwvervetegerw234332.csv",
            "File Description": "This file contains product details and order details.",
            "Key Columns": [
                {"Column Name": "product_id", "Description": "Unique identifier for each product."},
                {"Column Name": "product_name", "Description": "Name of the product."},
                {"Column Name": "unit", "Description": "Unit of the product."},
                {"Column Name": "product_type", "Description": "Type of the product."},
                {"Column Name": "brand_name", "Description": "Name of the product's brand."},
                {"Column Name": "manufacturer_name", "Description": "Name of the product's manufacturer."},
     
            ]
        }
            ]
}

