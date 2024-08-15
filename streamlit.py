import streamlit as st
import time
from openai import OpenAI
from elasticsearch import Elasticsearch

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

es_client = Elasticsearch('http://localhost:9200') 

def elastic_search(query, index_name="usermanual-answers1"):
    serach_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["description^3"],
                        "type": "best_fields"
                    }
                }
               
            }
        }
    }
    response = es_client.search(index=index_name,body=serach_query)
    
    response['hits']['hits']
    
    result_doc = []
    
    for hit in response['hits']['hits']:  
        result_doc.append(hit['_source'])
    return result_doc

def build_prompt(query,search_results):
    prompt_template =""" 
You are user manuel interpreter. Answer the QUESTION base on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.If CONTEXT doesn't contain  the answer output NONE


QUESTION: {question}

CONTEXT: {context}
""".strip()

    context  = ""
    for doc in search_results:
        context = context + f"title: {doc['title']}\ndescirption: {doc['description']}\n\n"
    
    prompt = prompt_template.format(question=query,context= context).strip()
    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='gemma2:2b',
        #model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


def rag(query):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)

    return answer

# Streamlit App
def main():
    st.title("Streamlit Application")

    # Input box
    user_input = st.text_input("Enter your input:")

    # Button to trigger the function
    if st.button("Ask"):
        with st.spinner('Processing...'):
            # Invoke the function with the input text
            output = rag(user_input)
            st.success(output)

if __name__ == "__main__":
    main()