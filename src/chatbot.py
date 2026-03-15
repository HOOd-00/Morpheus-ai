import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import Tool
from langchain.agents import create_agent
from src.config import GEMINI_API_KEY, BASE_DIR

# vector db path
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def get_agent_rag():
    
    # vector db and retriever
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")
    vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 15}) # Number of movies that will be retrevie

    # tools for llm
    def seach_movies_tools(query: str) -> str:
        docs = retriever.invoke(query)
        # concatnate output
        return "\n\n".join([doc.page_content for doc in docs])

    movie_tool = Tool(
        name="movie_database_search",
        description="MUST USE this tool when users ask for information about a movie, including its synopsis, genre, or filming techniques. Do not answer without using this tool.",
        func=seach_movies_tools
    )
    tools = [movie_tool] # can append more

    # LLM
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=GEMINI_API_KEY)

    prompt = """
    You are a professional Movie Expert and VFX Consultant.
    1. You MUST ALWAYS use the available tools to find information to answer the user's questions.
    2. DO NOT ask the user for more information, just search and provide the best recommendations based on the query.
    3. STRICT RULE: You MUST answer ONLY using the facts retrieved from the tool. If the retrieved data does not mention specific filming techniques, cameras, or VFX, DO NOT make them up from your general knowledge. Instead, just admit that you don't know.
    Answer in English language with a helpful and passionate tone.
    """

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt
    )

    return agent

if __name__ == "__main__":
    print("Morphues AI. is starting...")
    agent = get_agent_rag()
    print("\n Morphues: Ready! Enter you question to start.")
    
    while True:
        try:
            user_input = input("\n You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("\n Morphues: Stopping, Exit")
                break
                
            if not user_input.strip():
                continue

            print("\n Morphues: Thinking...")

            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            try:
                final_answer = result["messages"][-1].content
                if final_answer is None:
                    final_answer = "I could not find the information in the database."
            except (KeyError, AttributeError):
                final_answer = result

            print(f"\n Morphues: {final_answer}")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n Morphues: Stopping, Exit")
            break
        except Exception as e:
            print(f"Exception Error: {e}")