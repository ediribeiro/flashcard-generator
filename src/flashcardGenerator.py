# Library Imports
import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

load_dotenv()

# Load the OpenAI API key from an environment variable
openai_api_key = os.environ["OPENAI_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"]= "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')

# Initialize the ChatOpenAI model
llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model_name="gpt-3.5-turbo",
    temperature=0.6,
)

# Function to extract text from PDF based on start and end page numbers
raw_text = ""
def extract_text_from_pdf(uploaded_file, start_page, end_page):
    raw_text = ''
    pdf_title = uploaded_file.name.split(".")[0]
    with uploaded_file as file:
        pdf_reader = PdfReader(file)
        for i, page in enumerate(pdf_reader.pages):
            if i < start_page:
                continue
            if i >= end_page:
                break
            raw_text += page.extract_text() + "\n"
    return pdf_title, raw_text

#Production text chunks
def get_text_chunks(raw_text):
    text_splitter=CharacterTextSplitter(
        separator='\n',
        chunk_size=7000,
        length_function=len,
    )
    text_chunks=text_splitter.split_text(raw_text)
    print(len(text_chunks))
    return text_chunks

RESPONSE_JSON_STRUCTURE = {
  "1": {
    "pergunta": "Sua pergunta sobre o conceito do texto",
    "resposta": "A resposta para a sua pergunta"
  },
  "2": {
    "pergunta": "Sua pergunta sobre outro conceito",
    "resposta": "A resposta para a sua segunda pergunta"
  },
  # // ... e assim por diante para cada conceito identificado
}

prompt_template_flashcards = """
Texto Fornecido: {text}
Como especialista na criação de flashcards educacionais, sua tarefa é extrair os principais conceitos do texto fornecido e formular perguntas e respostas concisas.
Passos:
1. Identifique os conceitos principais ou temas do texto fornecido.
2. Formule uma pergunta clara e concisa para cada conceito principal ou tema, focando em facilitar a compreensão do texto.
3. Forneça uma resposta direta e sucinta para cada pergunta.
4. Retorne os flashcards gerados no formato JSON especificado:
{response_json}
Observação: A estrutura de resposta deve conter apenas as perguntas e respostas essenciais que refletem os conceitos principais.
"""

card_generation_prompt=PromptTemplate(
    input_variables=['text','response_json'],
    template=prompt_template_flashcards
)

card_chain=LLMChain(llm=llm,prompt=card_generation_prompt, output_key='cards',verbose=True)

def generate_flashcards(text_chunks):
    card_table_data = []
    response_json = json.dumps(RESPONSE_JSON_STRUCTURE)
    
    progress_bar = st.progress(0)  # Initialize progress bar
    
    for i, chunk in enumerate(text_chunks):
        response = card_chain({'text': chunk, 'response_json': response_json})
        card_str = response.get('cards')

        progress_bar.progress((i + 1) / len(text_chunks)) # Update progress bar

        try:
            card_list = json.loads(card_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from chunk: {e}")
            continue  # Skip this chunk and proceed with the next one

        for key, value in card_list.items():
            pergunta = value.get('pergunta')
            resposta = value.get('resposta')
            if pergunta and resposta:  # Ensure both pergunta and resposta are not None
                card_table_data.append({'pergunta': pergunta, 'resposta': resposta})
            else:
                print(f"Missing 'pergunta' or 'resposta' in chunk: {chunk}")
                
    return card_table_data

# Main function to run the Streamlit app
def main():
    st.title("Flashcard Generator")

    # File upload section
    uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
    if uploaded_file is not None:
        st.write("File Uploaded Successfully!")

        # Get start and end page numbers
        start_page = st.number_input("Start Page", min_value=1, step=1, value=1)
        end_page = st.number_input("End Page", min_value=1, step=1, value=10)

        # Button to generate flashcards
        if st.button("Generate Flashcards"):
            # Extract text from PDF based on page numbers
            pdf_title, raw_text = extract_text_from_pdf(uploaded_file, start_page, end_page)

            # Generate flashcards from text chunks
            text_chunks = get_text_chunks(raw_text)
            flashcards = generate_flashcards(text_chunks)

            # Display flashcards
            if flashcards:
                st.subheader("Generated Flashcards")
                df_flashcards = pd.DataFrame(flashcards)
                st.write(df_flashcards)
                st.download_button(
                    label="Download Flashcards CSV",
                    data=df_flashcards.to_csv().encode(),
                    file_name=f"{pdf_title}-flashcards.csv",
                    mime="text/csv"
                )

# Run the Streamlit app
if __name__ == "__main__":
    main()
