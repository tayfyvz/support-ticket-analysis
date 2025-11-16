"""Prompt templates for ticket classification and summarization."""

from langchain_core.prompts import ChatPromptTemplate

# Prompt for the "Map" step (classifying a single ticket)
CLASSIFY_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert ticket classifier. Classify the following ticket into a "
        "category (billing, bug, feature request, support, technical, account) and a "
        "priority (low, medium, high) based on its title and description.\n\n"
        "PRIORITY GUIDELINES:\n"
        "- HIGH: Critical issues affecting multiple users, security vulnerabilities, "
        "service outages, data loss/corruption, billing errors, account lockouts, "
        "or issues that completely block core functionality.\n"
        "- MEDIUM: Issues affecting some users but with workarounds, performance problems "
        "that degrade but don't block functionality, missing features that are important "
        "but not urgent, or bugs that impact non-critical features.\n"
        "- LOW: Minor bugs with easy workarounds, cosmetic issues, feature requests for "
        "nice-to-have enhancements, accessibility improvements that don't block usage, "
        "or issues affecting very few users.\n\n"
        "Be judicious with HIGH priority - most tickets should be MEDIUM or LOW. "
        "Only mark as HIGH if it's truly critical or blocking.\n\n"
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

