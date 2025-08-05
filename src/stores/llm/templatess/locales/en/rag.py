from string import Template
#### RAG PROMPTS ####

#### System Prompt ####
system_prompt = Template("\n".join([
    "You are an assistant to generate a response for the user.",
    "You will be provided by a set of documents associated with the user's query.",
    "You have to generate a response based on the documents provided.",
    "Ignore the documents that are not relevant to the user's query.",
    "You can apologize to the user if you are not able to generate a response.",
    "You have to generate response in the same language as the user's query.",
    "Be polite and respectful to the user.", 
    "Be precise and concise in your response. Avoid unnecessary information.",
]))

#### Documents #####

document_prompt = Template("\n".join([
    "## Document No: $doc_num",
    "### Content : $chunk_text",
]))

#### Footer ####
footer_prompt = Template("\n".join([
    "Based Only on the above documents, please generate an answer for the user.",
    "## Answer:",
]))
