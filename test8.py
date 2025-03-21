
from test5 import generate_response,pred_plots,graphs
from prompts_and_descriptions import csv_json
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from dotenv import load_dotenv
load_dotenv()
import pandas as pd 
import streamlit as st


def main():

    st.title("Streamlit App CSV2Pandas Query")

    # User Input
    question = st.text_input("Enter your question:")
    print(question)


    # pandas_query = generate_response("Give me the top 5 discounted products",csv_json)

    # feedback = input("Enter feedback or left empty ")
    # if feedback:
    #     query_feedback_checker(pandas_query,"",feedback)


    # question = 'top 10 unique product types and their count'

    if question:

        try:
            pandas_query = generate_response(question,csv_json)
            print(pandas_query)

            print("Python script saved as output_pandas_query.py")

            # code_filename = "output_pandas_query.py"
            st.write("### Output Code ")
            st.code(pandas_query['Pandas Query'], language="python") # Display the code

            if pandas_query is not None:
                st.write("### Output Data ")

                try:
                    df = pd.read_csv("output_second.csv")  # Load data from CSV
                    st.dataframe(df)   # Display the data

                    pred= None
                    pred = pred_plots(question, df)   # Predict the plot type
                    try:
                        Graph_code,image_path = graphs(pred, df)
                        st.markdown("<br>", unsafe_allow_html=True)  # HTML line break

                        # Display the Graph code
                        st.write("### Graph Code ")
                        st.code(Graph_code, language="python")

                        # Display the image
                        st.image(image_path, caption="Generated Graph", use_container_width=True)
                    except Exception as e:
                        Graph_code=None
                        st.error(f"Error in generating graph: {e}")

                except Exception as e:
                    st.error(f"Error in  Predicting Plots: {e}")
            else:
                st.warning("No data available.")


            formatted_code = highlight(pandas_query['Pandas Query'], PythonLexer(), TerminalFormatter())
            print(formatted_code)

            with open("output_pandas_query.py", "w") as file: # Saves the code to a file (output_pandas_query.py)
                file.write(pandas_query['Pandas Query'])
            with open("output_pandas_query.py", "a") as file:  # Appends the graph code to the file
                file.write("\n#Matplotlib Code for Plot\nimport pandas as pd\ndf = pd.read_csv('output_second.csv')" + Graph_code)
        except Exception as e:
            st.error(f"Error in Generatinng Code: {e}")
    

if __name__ == '__main__':
    print("Running main")
    # breakpoint()

    main()