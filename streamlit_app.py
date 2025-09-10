import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="RAG Document QA System",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 RAG Document QA System")
st.markdown("Upload documents and ask questions using AI-powered retrieval")

# Sidebar for system status
with st.sidebar:
    st.header("System Status")
    
    # Check backend connection
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Not Running")
        st.info("Make sure to run: `python backend/main.py`")
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Upload a PDF or TXT file")
    st.markdown("2. Wait for processing")
    st.markdown("3. Ask questions about the document")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Document Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt", "md"],
        help="Upload documents to create a knowledge base"
    )
    
    # Upload button and processing
    if uploaded_file is not None:
        st.info(f"📎 Selected: {uploaded_file.name}")
        
        if st.button("🚀 Process Document", type="primary"):
            try:
                # Prepare files for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Uploading document...")
                progress_bar.progress(25)
                
                # Upload to backend
                with st.spinner("Processing document..."):
                    response = requests.post(
                        "http://localhost:8000/upload",
                        files=files,
                        timeout=120  # 2 minute timeout for large files
                    )
                
                progress_bar.progress(75)
                status_text.text("Creating embeddings...")
                
                if response.status_code == 200:
                    result = response.json()
                    progress_bar.progress(100)
                    status_text.text("✅ Document processed successfully!")
                    
                    st.success("Document uploaded and processed!")
                    st.json(result)
                    
                    # Store in session state
                    st.session_state.document_uploaded = True
                    st.session_state.document_name = uploaded_file.name
                    st.session_state.upload_time = datetime.now()
                    
                else:
                    st.error(f"Upload failed: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Upload timeout. Try a smaller document or check your connection.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Make sure it's running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col2:
    st.header("❓ Ask Questions")
    
    # Check if document is uploaded
    if st.session_state.get('document_uploaded', False):
        st.success(f"📄 Document ready: {st.session_state.get('document_name', 'Unknown')}")
        
        # Question input
        question = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the main points discussed in this document?",
            height=100
        )
        
        # Predefined questions for quick testing
        st.markdown("**Quick Questions:**")
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            if st.button("📋 Summarize document"):
                question = "What are the main points and key information in this document?"
        
        with col_q2:
            if st.button("🔍 Key requirements"):
                question = "What are the main requirements or objectives mentioned?"
        
        # Ask button
        if st.button("🤔 Get Answer", type="primary", disabled=not question):
            if question.strip():
                try:
                    # Prepare request
                    payload = {"question": question.strip()}
                    
                    # Show loading state
                    with st.spinner("🧠 AI is thinking..."):
                        start_time = time.time()
                        response = requests.post(
                            "http://localhost:8000/ask",
                            json=payload,
                            timeout=60
                        )
                        response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display answer
                        st.markdown("### 💡 Answer:")
                        st.markdown(result.get('answer', 'No answer received'))
                        
                        # Display metadata
                        st.info(f"⏱️ Response time: {response_time:.2f} seconds")
                        
                        # Display source documents
                        source_docs = result.get('source_documents', [])
                        if source_docs:
                            st.markdown("### 📖 Source References:")
                            for idx, doc in enumerate(source_docs, 1):
                                with st.expander(f"📄 Source {idx}"):
                                    st.markdown(f"**Content:** {doc.get('content', 'N/A')}")
                                    if doc.get('metadata'):
                                        st.json(doc['metadata'])
                        
                        # Store in chat history
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({
                            'question': question,
                            'answer': result.get('answer'),
                            'timestamp': datetime.now(),
                            'response_time': response_time
                        })
                        
                    else:
                        st.error(f"❌ Error getting answer: {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout. The question might be too complex.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Cannot connect to backend.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a question")
    else:
        st.info("📤 Please upload a document first to start asking questions")

# Chat History Section
if st.session_state.get('chat_history'):
    st.markdown("---")
    st.header("💬 Chat History")
    
    for idx, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"Q{len(st.session_state.chat_history)-idx}: {chat['question'][:50]}..."):
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")
            st.caption(f"Asked at: {chat['timestamp'].strftime('%H:%M:%S')} | Response time: {chat.get('response_time', 0):.2f}s")

# Footer with system info
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("🤖 Powered by Langchain + OpenAI")

with col_footer2:
    if st.session_state.get('upload_time'):
        st.caption(f"📅 Document uploaded: {st.session_state['upload_time'].strftime('%H:%M:%S')}")

with col_footer3:
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.document_uploaded = False
        st.rerun()

# Custom CSS for better styling
st.markdown("""
<style>
.stButton > button {
    width: 100%;
}
.stSuccess {
    padding: 0.5rem;
    border-radius: 0.5rem;
}
.stError {
    padding: 0.5rem;
    border-radius: 0.5rem;
}
</style>
""", unsafe_allow_html=True)
