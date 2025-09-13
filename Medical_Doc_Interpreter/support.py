from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import os
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Prompt template (same as notebook) ---
_PROMPT = """
You are a medical assistant helping patients understand their lab test results.

For each lab test in the results, provide:
1. Test name
2. Result and normal range
3. Whether it is normal, low, or high
4. A short plain language explanation

At the end, add:
⚠️ Disclaimer: This explanation is for understanding purposes only and not medical advice.

Lab Results:
{lab_results}

Respond in a clear bullet-point format.
"""

def init_chain(model_name: str = "gpt-4o-mini", temperature: float = 0.0):
    """
    Initialize and return a LangChain 'chain' consisting of the prompt template piped to the LLM.
    Call once (e.g. at app startup) and reuse the returned chain for multiple files/requests.
    """
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    prompt = PromptTemplate(input_variables=["lab_results"], template=_PROMPT)
    chain = prompt | llm
    return chain

def _as_text(result) -> str:
    """
    Normalizes LangChain return objects into a plain string.
    Handles: str, AIMessage-like objects (with .content), or other objects.
    """
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    # LangChain chat responses often have .content
    if hasattr(result, "content"):
        return result.content
    if hasattr(result, "text"):
        return result.text
    # Fallback to string conversion
    return str(result)

def analyze_pdf_lab_report(
    pdf_path: str,
    chain = None,
    combine_chunks: bool = True,
    chunk_size: int = 800,
    chunk_overlap: int = 50,
    max_chunks: Optional[int] = None
) -> str:
    """
    Load a PDF lab report, split into chunks, call the provided chain (or initialize a default chain),
    and return the model's summary as a plain string.

    Args:
        pdf_path: path to a local PDF file.
        chain: a chain returned by init_chain(). If None, init_chain() will be called with defaults.
        combine_chunks: if True, concatenate all chunk texts into one prompt; if False, summarize each chunk separately and join.
        chunk_size / chunk_overlap: text splitter settings.
        max_chunks: optionally limit number of chunks (useful for very large PDFs).

    Returns:
        A string containing the LLM-generated explanation (the chain output).
    """
    if chain is None:
        chain = init_chain()

    # 1) Load PDF pages as Document objects
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2) Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)

    if max_chunks is not None:
        chunks = chunks[:max_chunks]

    if not chunks:
        return "No text found in PDF."

    if combine_chunks:
        # Combine all chunks into one big prompt (simple approach; ok for short lab reports)
        combined_text = "\n\n".join([c.page_content for c in chunks])
        result = chain.invoke({"lab_results": combined_text})
        return _as_text(result)

    else:
        # Summarize each chunk separately and join results
        part_texts = []
        for c in chunks:
            res = chain.invoke({"lab_results": c.page_content})
            part_texts.append(_as_text(res))
        # Join per-chunk summaries. You can later send this to another chain for consolidation.
        return "\n\n".join(part_texts)

# Example usage (in your app.py):
# from support import init_chain, analyze_pdf_lab_report
# chain = init_chain()
# summary = analyze_pdf_lab_report("temp.pdf", chain)

# print(summary)





