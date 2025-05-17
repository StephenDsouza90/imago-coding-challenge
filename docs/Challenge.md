# Coding Challenge C3

Hello! 👋🏼

Thank you for taking on this task. Our goal is to better understand your hands-on development skills and workflow.

The following task is designed to evaluate key skills we consider essential for this position. There is no single correct solution, so feel free to approach it in the way you believe is best. Use your judgment and what you know about IMAGO so far. We're particularly interested in your thought process, so please support your ideas with clear and well-reasoned arguments.

We kindly ask you to submit your solution as a PDF. You're welcome to include links to tools like CodeSandbox, GitHub Pages, or any other relevant platform. The deadline for submission is 7 working days from the date you receive this challenge. If you need more time, don't hesitate to contact us to request an extension. We estimate this task should take approximately 4 hours to complete.

We hope you enjoy the challenge.

Best of luck! 🍀

## The Challenge

Your goal is to demonstrate how you would design and implement a system that retrieves media content (already stored in Elasticsearch) and serves it to users in a user-friendly way. Focus more on a robust backend service. There is no single correct solution and we are most interested in how you reason about the problem, structure your code, and handle real-world complexities like unstructured data, scalability, and testing.

### Requirements

- **Use our Test Elasticsearch Server**
    - Host: https://5.75.227.63
    - Port: 9200
    - Index: imago
    - Authenticate with basic authorization:
        - user: elastic
        - password: password
    - If there is an issue with the SSL certificate, please ignore it while sending the http request.
- **Media URLs**
    - To build a url to display a media thumbnail follow the formula: `BASE_URL . "/bild/" . DB . "/" . MEDIA_ID`
    - The result can look like this: https://www.imago-images.de/bild/st/0258999077/s.jpg
    - DB values are normally "st"/"sp" in ES docs
    - For the url media id needs to be 10 chars long, padded with zeroes at the start of the string if too short.
- **Search and Retrieval**
    - Retrieve media records from the existing Elasticsearch index.
    - Perform keyword-based search or filtering on fields such as title, description, or other metadata.
- **Data Normalization**
    - Handle unstructured or missing fields gracefully.
    - Propose any transformations you find useful to improve searchability or data quality.
- **API**
    - Create a robust backend API (Python) that provides search and filtering endpoints for consumers.
- **Problem Identification & Solution Proposal**
    - Identify a potential issue with the system setup (e.g., data inconsistencies, performance bottlenecks, security concerns).
    - Clearly articulate why this is a problem and how it could impact the system.
    - Propose a thoughtful solution and justify why it would be effective.
- **Scalability & Maintainability**
    - Discuss how your solution would handle large volumes of data.
    - Explain how you would keep your solution maintainable as more external providers and media items come online.
- **Monitoring & Testing**
    - Include basic monitoring or logging considerations.
    - Write tests that reflect your normal coding practices.

## Deliverable

Besides ElasticSearch you are free to use the tools and frameworks of your choice.

Keep in mind that we do not expect a production-ready application. Instead, we aim to gain insights into your typical working style, thought process, and approach to testing and quality standards. If there are elements you would typically include but that fall outside the scope or time constraints of this exercise, please document them or provide partial examples.

Please include the following:

- A README or similar document outlining your high-level thoughts, considerations, assumptions, and any limitations in your submission.
- A link to a Git repository or a zip file containing the executable code for your solution.
- A link to your deployed solution, an executable CodeSandbox, or clear instructions on how to run your provided code locally.

We hope you enjoy the challenge.

Thank you for your time! 😊