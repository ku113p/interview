"""Process modules for the interview application.

Contains 4 independent async processes:
- auth: Exchange external user IDs for internal user_ids
- transport: CLI and Telegram transports
- interview: Main graph worker for message processing
- extract: Knowledge extraction from completed areas
"""
