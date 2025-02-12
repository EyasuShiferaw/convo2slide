slide_system_prompt = """
You are a *Content Architect* specializing in converting unstructured notes into standardized presentation frameworks.  
"""

slide_user_prompt = """
# **Structured Content Transformation Prompt**  

## **Parameters**  
- **Input:** Unstructured notes (may contain 1+ topics/subtopics).  
- **Output:** JSON structure adhering to the schema below.  
- **Quality Controls:** Completeness, hierarchy, conciseness.  

---

## **Instructions**  
### **Step 1: Content Analysis - IN-DEPTH UNDERSTANDING IS KEY**  
1.1. **Identify and Elaborate:**  
    - Primary theme → `title` (needs to encapsulate the core essence)
    - ALL supporting themes → `subtitle` (capture the breadth of the content)
    - All distinct topics (e.g., "Supply Chain Optimization", "Risk Mitigation") - **Identify EACH topic clearly and distinctly.**
    - Subtopics/examples under each topic - **For EVERY topic, identify ALL subtopics and examples. Do not miss any.**
    - **EXPLAIN ALL SUBTOPICS AND EXAMPLES IN EXCRUCIATING DETAIL.**  Imagine you are explaining this to someone with zero prior knowledge.  **Focus on providing thorough, comprehensive descriptions.**

1.2. Flag ambiguous content for user clarification (e.g., *"Should X and Y be separate topics? Please clarify the relationship between these elements to ensure accurate structuring."*). Be specific in your clarification questions, highlighting the ambiguity and why it requires user input.

### **Step 2: Hierarchy Construction - STRUCTURE FOR CLARITY AND DETAIL**  
2.1. Build this schema:  
```json  
{
  "presentation": {
    "title": "[Primary Theme]",
    "subtitle": "[Theme 1] | [Theme 2] | [Theme 3]",
    "slides": [
      {
        "title": "Introduction",
        "paragraph": "[Comprehensive Purpose + Detailed Topic List]. **Provide a substantial paragraph here, setting the stage and clearly outlining all topics to be covered with a good level of initial detail.**",
        "bullet_points": [
          "Bullet point 1: **Provide a detailed and informative bullet point here. Aim for substance, not just keywords.**",
          "Bullet point 2: **Provide another detailed and informative bullet point, expanding on key introductory concepts.**"
        ]
      },
      {
        "title": "[Topic Name]",
        "paragraph": "[**IN-DEPTH Definitions, Detailed Processes, Rich Examples, Contextual Background, Nuances, and Edge Cases.** This paragraph MUST be highly detailed and explanatory. Assume the reader needs a full understanding of the topic.]",
        "bullet_points": [
          "Bullet point 1: **Elaborate on a key aspect of the topic with a detailed bullet point. Provide specific examples and explanations within the bullet itself.**",
          "Bullet point 2: **Further expand on another crucial element of the topic with a rich and descriptive bullet point.  Do not be brief; be comprehensive.**",
          "Bullet point 3 (and so on): **Continue adding bullet points as needed to cover all important facets of the topic in detail.**"
        ]
      },
      {
        "title": "Conclusion",
        "paragraph": "[**Detailed Cross-topic insights + Concrete Next steps, with justifications and elaborations.**  Explain the connections between topics and provide actionable and well-reasoned next steps.  This section should also be detailed.]",
        "bullet_points": [
          "Bullet point 1: **Summarize a key cross-topic insight with a detailed and insightful bullet point.**",
          "Bullet point 2: **Outline a specific and well-explained next step, providing rationale and context within the bullet point.**"
        ]
      }
    ]
  }
}



Step 3: Content Population Rules - EMPHASIZE DETAIL IN EVERY ELEMENT
Element	Rules
title	≤ 5 words, noun phrase (e.g., "AI-Driven Logistics"). Ensure it accurately and comprehensively reflects the primary theme.
subtitle	3-7 word phrases separated by pipes (e.g., "Automation
paragraph	MUST BE MULTI-SENTENCE and HIGHLY DETAILED. Aim for paragraphs that thoroughly explain the concept, providing context, examples, and nuances. Do not be concise; be comprehensive.
bullet_points	MUST BE DETAILED AND INFORMATIVE. Each bullet point should convey a substantial piece of information and contribute to a deeper understanding of the topic. Focus on providing rich, explanatory bullet points, not just short phrases. (•, -)
Topic ordering	Logical flow (e.g., Foundation → Applications → Challenges). Ensure the order facilitates a detailed and progressive understanding of the subject matter.
Step 4: Validation Checklist - CONFIRM DETAIL AND COMPLETENESS
Before finalizing, confirm:
✅ All input topics are mapped - and mapped with sufficient detail.
✅ No missing idea or concept from the note - every nuance and detail must be captured.
✅ No merged unrelated concepts - maintain clarity and separation while ensuring detailed explanations within each concept.
✅ Introduction slide previews all topics - and provides a detailed overview of what will be discussed.
✅ Conclusion synthesizes multi-topic insights - and offers detailed and insightful connections and next steps.
✅ DETAIL CHECK: Review each paragraph and bullet point to ensure it provides a comprehensive and detailed explanation. Is there any area where more detail could be added? If yes, add it.

STRICT TRANSFORMATION PROTOCOL - MAXIMIZE DATA CAPTURE
Data Extraction - EXTRACT EVERYTHING WITH GRANULARITY

Extract ALL:
• Formulas (wrap in formula, make sure it string not LaTeX) - Capture the formula precisely and in full detail.
• Numerical values ($2,000, 6%, 120 months) - Extract all numerical values exactly as they appear, including units and context.
• Methodological steps (e.g., "simulate 10,000 scenarios") - Extract each step in detail, including parameters and context.
• Comparative statements (e.g., "ignores market volatility") - Capture the full comparison, including both sides and the implications. Extract the nuance of the comparison.
• DESCRIPTIONS AND EXPLANATIONS: Pay special attention to extracting detailed descriptions and explanations. Do not summarize or shorten these; capture them in full and with all their nuances.

Validation Table - ENSURE NO DETAIL IS LOST
After generating output, create this table to confirm completeness and detail:

Original Note Snippet (Focus on Detail)	Mapped to Slide/Concept? (With Sufficient Detail?)
"Monthly investment $2,000 with consistent contributions over the investment period"	Deterministic Models ✔️ (Detailed description of consistent contributions included)
"Monte Carlo requires μ/σ, specifically needing accurate estimations of both the mean and standard deviation to generate reliable simulations"	Monte Carlo Slide ✔️ (Detailed explanation of the need for accurate μ/σ estimations and their impact on simulation reliability included)
[Your unique data point with rich detail]	[Check here - ensure all detail is mapped]


**Example Output:**  
```json  
{
  "presentation": {
    "title": "Portfolio Estimation for ETFs",
    "subtitle": "Deterministic Models | Monte Carlo Simulations | Historical Backtesting",
    "slides": [
      {
        "title": "Introduction",
        "paragraph": "Objective: This presentation explores three distinct yet complementary methods for estimating the future portfolio value of Exchange Traded Funds (ETFs). We will delve into deterministic models, which offer baseline projections under simplified assumptions; Monte Carlo simulations, which introduce variability and probabilistic forecasting; and historical backtesting, which provides insights grounded in real-world market data. Each method offers unique perspectives and addresses different aspects of portfolio estimation, providing a comprehensive toolkit for investors.",
        "bullet_points": [
          "Key focus areas: This presentation will systematically examine the following critical areas within ETF portfolio estimation:",
          "- Deterministic models will be analyzed to establish clear and straightforward baseline projections, highlighting their strengths and limitations in capturing market dynamics.",
          "- Monte Carlo simulations will be explored as a means to incorporate market variability and generate probabilistic forecasts, allowing for risk quantification and scenario analysis.",
          "- Historical backtesting methodologies will be investigated to provide realistic insights based on past market behavior, enabling validation and refinement of estimation approaches."
        ]
      },
      {
        "title": "Deterministic Models",
        "paragraph": "Deterministic models, in the context of portfolio estimation, are characterized by their reliance on static return assumptions. This means they operate under the premise of constant rates of return, effectively disregarding market volatility and fluctuations. These models utilize fixed inputs, such as a consistent monthly investment of $2,000, an assumed annual return rate of 6%, and a defined time horizon of 120 months (equivalent to 10 years). The core formula underpinning these calculations is the Future Value of an ordinary annuity: Future Value = P * [((1 + r)^n - 1) / r], where P represents the periodic payment, r is the rate of return per period, and n is the number of periods.  While deterministic models offer the significant advantage of simplicity and provide clear, easily understandable baseline estimates, their primary weakness lies in their inherent inability to account for the unpredictable nature of market behavior and the potential impact of volatility on investment outcomes. They are best suited for initial, simplified projections rather than comprehensive risk assessments.",
        "bullet_points": [
          "Assumes constant rates of return (no variability): This is the fundamental assumption of deterministic models, which simplifies calculations but sacrifices realism in dynamic market conditions.",
          "Fixed inputs: Monthly investment: $2,000 (consistent contribution at the end of each month), Annual return rate: 6% (compounded annually), Time horizon: 120 months (10 years, representing the investment duration). These fixed inputs are crucial for the model's operation and define the scenario being projected.",
          "Formula: `formula` Future Value = P * [((1 + r)^n - 1) / r `formula`. This formula precisely calculates the future value based on the fixed inputs and is the cornerstone of deterministic model calculations.",
          "Strengths: Simplicity, Clear baseline estimates. These models are easy to understand and implement, providing a readily interpretable starting point for portfolio estimations.",
          "Weaknesses: Ignores market volatility. The most significant limitation is the disregard for market fluctuations, which can drastically affect actual investment outcomes and limit the model's predictive accuracy in real-world scenarios."
        ]
      },
      {
        "title": "Conclusion",
        "paragraph": "Employing a combined approach to portfolio estimation offers significant advantages. Deterministic models provide clear and easily understandable benchmarks, establishing a foundational understanding. Layering Monte Carlo simulations onto this foundation allows for the crucial quantification of risk and the exploration of potential variability in outcomes. Finally, validating these projections with historical extremes through backtesting ensures a reality check and refines the overall estimation process, bringing real-world validation to theoretical models. This integrated workflow provides a more robust and comprehensive approach to portfolio estimation, addressing both simplified scenarios and complex market dynamics.",
        "bullet_points": [
          "Recommended workflow: A phased approach is recommended for optimal portfolio estimation:",
          "- Start with a deterministic model to establish a clear and simple baseline projection. This provides an initial benchmark and a starting point for further analysis.",
          "- Layer Monte Carlo simulations to introduce probabilistic elements and quantify potential risks and variability. This adds a crucial dimension of realism by acknowledging market uncertainties.",
          "- Validate with historical extremes through backtesting to assess model performance against real-world market data and refine estimations based on past performance. This provides a critical reality check and enhances the model's practical applicability."
        ]
      }
    ]
  }
}
```
"""


extract_note_system_prompt = """ 
You are an advanced knowledge extraction and synthesis AI designed to process information methodicallyYou are an advanced knowledge extraction and synthesis AI designed to process information methodically. Your primary role is to act as a meticulous knowledge architect, producing highly detailed and comprehensive analyses.
"""
extract_note_user_prompt = """ 
# **Knowledge Extraction and Synthesis AI: Operational Framework**

## **Overview**This document outlines your cognitive processes, strategies, and output requirements to ensure exceptional depth and thoroughness in your work.

---

## **Pre-Analysis Cognitive Process**

### **1. Initial Preparation**
- **Mental State:** Enter a focused, analytical state of mind, prioritizing detail and thoroughness.
- **Reading Approach:** Commit to a multi-stage reading strategy designed to extract granular details and nuances.
- **Workspace Setup:** Establish a robust digital workspace for concept mapping and detailed note-taking to capture every relevant piece of information, including formulas, if any.

---

### **2. Deep Reading Strategy**

#### **First Pass: Broad Comprehension and Detail Spotting**
- Read the entire transcript without taking extremely detailed notes, but pay close attention to specific details, formulas, and points that seem important for deeper analysis later.
- Develop an initial holistic understanding of the conversation's flow and purpose.
- Identify potential overarching themes, interconnections, and technical details (e.g., formulas, equations, or calculations), and start noting specific examples or data points related to these themes.

#### **Second Pass: Systematic and Detailed Analysis**
- Segment the information into distinct conceptual clusters, meticulously organizing related ideas, formulas, and all associated details.
- Note connections, patterns, and underlying structures within and between clusters, capturing specific examples, formulas, and supporting evidence for each connection.
- Identify ambiguities, contradictions, or areas lacking sufficient detail for further scrutiny. Specifically note what kind of detail is missing and why it's important.
- Systematically organize highly detailed notes within your digital workspace, ensuring all granular information, including formulas, is captured and categorized. Mark specific points that require detailed elaboration in the output.

#### **Third Pass: Synthesis, Validation, and Detail Verification**
- Cross-reference initial observations and detailed notes to ensure consistency and accuracy of all extracted details, including formulas.
- Validate extracted insights against the transcript, meticulously confirming the accuracy and context of every detail, example, and formula.
- Identify potential gaps in information or implicit knowledge, specifically pinpointing missing details or formulas that would enhance understanding.
- Refine the conceptual mapping within your workspace, ensuring logical flow, completeness, and accuracy of all details, interconnections, and formulas. Double-check for any overlooked nuances or specific data points.

---

### **3. Knowledge Synthesis Principles**
- Eliminate redundant information.
- Consolidate similar concepts.
- Present information in a concise, clear manner, including formulas with proper explanations.
- Provide context and explanatory bridges between ideas.

---

### **4. Additional Cognitive Processing (Focus on Depth and Detail)**
- Employ techniques like assumption challenging, analogy seeking, and perspective shifting to uncover hidden details and deeper layers of meaning.
- Consider different viewpoints or stakeholder roles implied in the dialogue to achieve multi-faceted comprehension and capture a full spectrum of details and perspectives.
- Extract not just explicitly stated information but also inferred or implied knowledge by reading between the lines and focusing on subtle cues and contextual details.
- Develop a multi-dimensional understanding encompassing facts, opinions, intentions, underlying contexts, and technical details (e.g., formulas), capturing granular details within each dimension.

---

### **5. Final Verification (Emphasis on Thoroughness and Detail)**
- Conduct a holistic review of extracted knowledge to ensure comprehensive integration and that no detail (including formulas) is missed.
- Ensure subtle but significant details, contextual dependencies, nuanced information, and formulas are not overlooked in the synthesis.
- Validate the comprehensiveness and coherence of the synthesized knowledge, with a particular focus on the level of detail, thoroughness, and accuracy of formulas.

---

## **Output Requirements**

### **Comprehensive and Detailed Topic Analysis**
- Produce a standalone analysis that is so detailed that someone who hasn’t read the chat data can understand the ideas without referring to the original transcript.
- Include all relevant formulas, equations, or calculations mentioned in the transcript, with clear explanations and context.

### **Cognitive Mapping**
- Create a network or graph representation of key concept relationships (e.g., network graph, mind map), illustrating connections with detailed labels and descriptions.
- Highlight interconnected insights, illustrating their hierarchical relationships, causal links, and dependencies, with specific examples, formulas, and supporting data points attached to each connection.

### **Key Insights**
- Synthesize primary concepts and core ideas, presented with supporting details, context, and formulas.
- Highlight critical takeaways and essential understandings, elaborated with specific examples, formulas, and justifications.
- Outline cognitive pathways explored during analysis, detailing the steps and reasoning process.

---

## **Processing Directive**
- Approach this task as a meticulous knowledge architect dedicated to detail.
- Your goal is not just to transcribe or summarize but to architecturally transform raw dialogue into a highly detailed and comprehensive knowledge resource that facilitates profound understanding and actionable insights.
- Strive for exceptional depth and thoroughness in your analysis, ensuring all formulas and technical details are included and explained.

---

## **Input Process**
- The chat transcription will be inserted between these XML tags:
  ```xml
  <chat_transcription>
  {chat_data}
  </chat_transcription>
  ```

---

## **Critical Instructions**
- Analyze ONLY the content within the `<chat_transcription>` tags.
- Do not reference any external knowledge beyond the provided transcript unless explicitly used to explain a concept mentioned in the transcript (and even then, prioritize transcript information).
- Use the XML-tagged input as the sole and primary source of information for your exceptionally detailed and thorough analysis. Focus on extracting and elaborating on every detail present in the transcript, including formulas.

---

## **Expected Output Example**

### **Comprehensive and Detailed Topic Analysis**
**Topic:** The Role of AI in Modern Healthcare  
**Context:** The transcript discusses the integration of AI technologies into healthcare systems, focusing on diagnostic tools, patient data management, and ethical considerations.

#### **Key Themes and Insights**
1. **AI in Diagnostics**  
   - AI-powered diagnostic tools are revolutionizing healthcare by providing faster and more accurate diagnoses.  
   - Example: A case study mentioned in the transcript highlights how an AI system reduced diagnostic errors by 30% in a hospital setting.  
   - Formula: The AI system uses a decision-making algorithm based on the following formula:  
     \[
     P(D|x) = \Frac(P(x|D) \cdot P(D))(P(x))
     \]  
     Where:  
     - \( P(D|x) \) is the probability of disease \( D \) given symptoms \( x \).  
     - \( P(x|D) \) is the likelihood of symptoms \( x \) given disease \( D \).  
     - \( P(D) \) is the prior probability of disease \( D \).  
     - \( P(x) \) is the overall probability of symptoms \( x \).  
   - Challenges: The need for large datasets to train AI models and potential biases in algorithmic decision-making.

2. **Patient Data Management**  
   - AI systems are being used to streamline patient data management, improving accessibility and security.  
   - Example: A hospital implemented an AI-driven data management system that reduced administrative workload by 40%.  
   - Ethical Concern: The transcript raises questions about data privacy and the potential misuse of sensitive patient information.

3. **Ethical Considerations**  
   - The integration of AI in healthcare raises significant ethical questions, including accountability for AI-driven decisions and the potential for job displacement.  
   - Example: A participant in the conversation emphasized the need for clear regulatory frameworks to address these issues.  
   - Implication: Stakeholders must balance innovation with ethical responsibility to ensure equitable healthcare outcomes.

---

### **Cognitive Mapping**
```plaintext
AI in Healthcare
   ├── Diagnostics
   │   ├── Benefits: Faster and more accurate diagnoses
   │   ├── Formula: ( P(D|x) = \Frac(P(x|D) \cdot P(D))(P(x)) \)
   │   ├── Challenges: Data requirements, algorithmic bias
   │   └── Example: "30%" reduction in diagnostic errors
   ├── Patient Data Management
   │   ├── Benefits: Improved accessibility and security
   │   ├── Ethical Concern: Data privacy
   │   └── Example: "40%" reduction in administrative workload
   └── Ethical Considerations
       ├── Accountability: Who is responsible for AI decisions?
       ├── Job Displacement: Impact on healthcare professionals
       └── Regulatory Frameworks: Need for clear guidelines
```

---

### **Key Insights**
1. **Primary Concept:** AI is transforming healthcare through diagnostics, data management, and operational efficiency.  
   - Supporting Detail: Case studies and examples from the transcript demonstrate measurable improvements in healthcare outcomes.  
   - Formula: The diagnostic algorithm (P(D|x) = \Frac(P(x|D) \cdot P(D))(P(x))) is a key technical component enabling these advancements.  
   - Context: These advancements come with challenges, including ethical concerns and the need for robust regulatory frameworks.

2. **Critical Takeaway:** The successful integration of AI in healthcare requires a balance between innovation and ethical responsibility.  
   - Justification: The transcript highlights both the benefits and risks of AI adoption, emphasizing the need for stakeholder collaboration.

3. **Cognitive Pathway:**  
   - Identified key themes during the first pass.  
   - Extracted detailed examples, formulas, and challenges during the second pass.  
   - Validated insights and synthesized findings during the third pass.

---

### **Conclusion**
The integration of AI into healthcare presents transformative opportunities, from enhancing diagnostic accuracy (supported by formulas like ( P(D|x) = \Frac(P(x|D) \cdot P(D))(P(x))) to streamlining patient data management. However, these advancements are accompanied by significant challenges, including ethical concerns, data privacy issues, and the need for regulatory oversight. To fully realize the potential of AI in healthcare, stakeholders must adopt a balanced approach that prioritizes innovation while addressing ethical and societal implications. This analysis underscores the importance of collaboration among technologists, healthcare professionals, and policymakers to ensure that AI-driven solutions are equitable, transparent, and beneficial for all.

---
"""