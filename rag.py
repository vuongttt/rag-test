from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI

from langchain_openai import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002",
    openai_api_version="2023-05-15",
)


vectordb = Chroma(persist_directory="/Users/renatomoretti/Desktop/RAG/8meta_chroma_db", embedding_function=embeddings)
sources = set()
for e in vectordb.get():
    sources.add(e.metadata.get("source", ""))
print(f"SOURCE: {sources}")

PROMPT_TEMPLATE = """

Act as a helpful technical assistant that guides users finding information about alarms within the section "Alarm Activation Diagram" in the document provided.
This is the logic of your interaction with the user and the documentation.

Step 1:
a. You'll receive an alarm code "{question}".
b. Try to find the answer in the section "Alarm Activation Diagram" of the {context}.
c. Report the relevant content as stated in the table.
d. Report the content in form of table.

"""

model = AzureChatOpenAI(openai_api_version="2023-05-15", azure_deployment="gpt-4-32k")

from langchain.prompts import ChatPromptTemplate


def answer(query_text, serial_number, threshold=0.6):
    new_query_text = """
    WRITE YOUR PROMPT HERE {question}
    """
    new_query_text_prompt_template = ChatPromptTemplate.from_template(new_query_text)
    new_query_text_prompt = new_query_text_prompt_template.format(question=query_text)
    print(f"query text: {new_query_text_prompt}")
    results = vectordb.similarity_search_with_relevance_scores(new_query_text, k=5, filter={
        "source": f"/Users/renatomoretti/Desktop/BrewBot/8files/{serial_number}.pdf"})
    print(f"source_file: /Users/renatomoretti/Desktop/BrewBot/8files/{serial_number}.pdf")
    print(len(results))
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    response_text = model.predict(prompt)

    # sources = [doc.metadata.get("source", None) for doc, _score in results]
    print([doc.metadata for doc, _score in results])
    pages = [doc.metadata.get("page", 0) for doc, _score in results]
    pages = [e for e in pages if e != 0]
    pages.sort()
    # formatted_response = f"Response: {response_text}\nSources: {sources}"
    formatted_response = f"Response: {response_text}"
    print(formatted_response)
    return formatted_response, pages
