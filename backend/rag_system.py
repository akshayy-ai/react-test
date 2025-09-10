from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from typing import Dict, Any

class RAGSystem:
    def __init__(self, vectorstore: Chroma = None):
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Custom prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Use the following context to answer the question. If you don't know the answer 
            based on the context, say so clearly.

            Context: {context}

            Question: {question}

            Answer: """
        )
    
    def set_vectorstore(self, vectorstore: Chroma):
        """Set the vector store"""
        self.vectorstore = vectorstore
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer"""
        if not self.vectorstore:
            raise ValueError("No document has been uploaded yet")
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
        # Get answer
        result = qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        }
