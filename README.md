# swissAIhackaton
AI assistive chatbot that gives instructions to anyone about three cantons of Switzerland: Zurich, Vaud, Neuchâtel. We used RAG assistant and Apertus open source.


## SwissAI Civic Chatbot

Our project originates from a personal need: as international students, we have experienced firsthand how challenging it can be to navigate bureaucracy, regulations, and logistical procedures 
in a new country. Often, you don’t know who to turn to for practical questions, and the risk is getting lost among dozens of websites, PDFs, and regulations.

That’s why we envisioned a digital assistant acting as a “civic friend”: an accessible, transparent, and reliable chatbot that provides clear answers to questions about permits, registrations, 
tuition fees, transportation, and more. Our vision is to connect the assistant to a phone number / WhatsApp, so you can interact with it just like a real friend ready to help you.

### Scalability

The current prototype works with documents from 3 cantons (Vaud, Zurich, Neuchâtel), but its architecture is scalable at the national level: 
- thanks to the RAG (Retrieval-Augmented Generation) paradigm, it is enough to add new official documents to extend coverage to the other 23 cantons, without retraining from scratch;
- the system can easily adapt to new thematic areas (e.g., healthcare, taxes, transportation) and to multiple national languages (IT, FR, DE, EN);
- in the future, the knowledge base could update automatically by monitoring the official portals of the cantons (HTML, open data, regulations), thus ensuring information that is always up-to-date and reliable.

### Transparency and Trustworthiness

A fundamental principle of the project is trust:
- Each answer is accompanied by official references (title, link, document page).
- If the information is not available in the documents, the chatbot explicitly states it and redirects users to the relevant offices.
- This ensures verifiable answers, avoiding the risk of AI model “hallucinations.”

### Business Model and Future Vision

Our project features a sustainable, scalable business model, capable of serving a market estimated at over 1 billion CHF:
- Public administrations could adopt it as a digital front-end to reduce the costs of counters and call centers.
- Universities, companies, and organizations for international mobility could integrate it as an additional service for students and foreign workers.
- Premium services (multilingual support, priority assistance, integration with automated procedures, real-time updates) could generate sustainable revenue streams.
The chatbot is not just a technical project, but a step toward a national ecosystem of digital civic assistance, built on transparency, reliability, and universal accessibility.


# Backend pipeline








# General pipeline frontend

![Screenshot del workflow](https://github.com/user-attachments/assets/22ddc4c1-1f67-4cbe-97b4-a6824a8e2c21)


