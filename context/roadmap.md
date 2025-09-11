### Vision Statement
To create a richly-proactive AI email inbox assistant that seamlessly integrates with a user's existing workflow, reducing overhead and adding meaningful, actionable value through intelligent automation. The assistant should feel like an extension of the user's own mind, mapped onto the domain of email efficiency.

---

### Phase 1: Meta-Project Enhancements (Complete)

-   **[COMPLETED]** **Robust Logging System:**
    -   **Description:** Implemented a new, resilient command logging system. It uses a Python helper script to ensure the session history JSON is always valid and stores SHA256 hashes of command outputs to prevent uncontrolled file growth.
    -   **Impact:** This provides a stable foundation for all meta-cognitive features of the Loop.

-   **[COMPLETED]** **Handoff Visualization:**
    -   **Description:** Created a script to generate a PNG image visualizing the chronological flow of handoff files. This allows for a clear, high-level overview of the agent's work across sessions.
    -   **Impact:** Improves observability and understanding of the Loop's "thought process".

---

### Phase 2: Inbox Assistant - Core Features (Complete)

-   **[COMPLETED]** **Efficient AI Triage:**
    -   **Description:** Refactored the email categorization logic. The system now fetches all of a message's labels (including user-defined ones) from the Gmail API. It attempts to derive a category from these labels first, only using the Gemini API as a fallback if a clear category isn't present.
    -   **Impact:** Reduces API costs, respects the user's existing organizational workflow, and uses AI for targeted, high-value tasks.

-   **[COMPLETED]** **Interactive Generative Replies:**
    -   **Description:** Implemented a feature to generate suggested email replies. Users can regenerate drafts with different `tone` (casual/formal) and `detail` (concise/elaborate), and can provide a custom text prompt for further guidance.
    -   **Impact:** Provides users with fine-grained control over AI-generated content, making the feature more flexible and useful.

---

### Phase 3: Future Brainstorming & Innovations (Next Up)

-   **[NEXT]** **Calendar-Aware Scheduling:**
    -   **Concept:** When an email's content involves scheduling, the assistant could automatically check the user's Google Calendar for availability. Suggested replies could then include options like "Yes, I'm free then. I've drafted a confirmation and calendar invite for you to review."
    -   **Value:** Eliminates the context-switching and manual effort of checking a calendar to reply to an email.

-   **[IDEA]** **Unified Search Assistant:**
    -   **Concept:** Enhance the search functionality to be a true "assistant". A user could search for "Q3 marketing project", and the backend would perform a federated search across Gmail, Google Drive, and Google Calendar, using Gemini to synthesize the results into a single, actionable summary.
    -   **Value:** Breaks down information silos between Google services, providing a unified view of a project or topic.

-   **[IDEA]** **Proactive Action Items:**
    -   **Concept:** The AI could detect actionable phrases in emails (e.g., "Could you send me the report?", "I'll follow up next week") and automatically create tasks in a list or even draft calendar reminders for the user to approve.
    -   **Value:** Moves from a passive assistant to a truly proactive one that helps manage commitments.
