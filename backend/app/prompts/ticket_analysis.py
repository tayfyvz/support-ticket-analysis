"""Prompt templates for ticket classification and summarization."""

from langchain_core.prompts import ChatPromptTemplate

# Prompt for the "Map" step (classifying a single ticket)
CLASSIFY_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert ticket classifier. Classify the following ticket into a "
        "category (billing, bug, feature_request, support, technical, account) and a "
        "priority (low, medium, high) based on its title and description. "
        "Optionally provide notes with additional insights, recommendations, or important details. "
        "Only include notes if they add value - leave notes empty if not needed. "
        "Respond using the provided tool."
    ),
    ("human", "Ticket Title: {title}\n\nTicket Description: {description}")
])

# Prompt for the "Reduce" step (summarizing all tickets)
SUMMARY_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Generate a concise, one-paragraph executive summary "
        "of the following batch of processed tickets. Highlight any major themes, "
        "common categories, or urgent (high-priority) issues."
    ),
    ("human", "Here are the processed tickets:\n\n{tickets_as_string}")
])

