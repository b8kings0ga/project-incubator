import re
from collections import Counter

# Create a list of AI topics and trends from the research papers and news articles
ai_research_topics = [
    "Large Language Models (LLMs)",
    "Generative AI",
    "AI Agents",
    "Multimodal AI",
    "Small Language Models",
    "AI Ethics",
    "AI Alignment",
    "Reinforcement Learning",
    "Explainable AI",
    "Self-Supervised Learning",
    "AI for Science",
    "AI for Climate",
    "Robotics",
    "Computer Vision",
    "Natural Language Processing",
    "AI Safety",
    "Quantum AI",
    "AI Regulation",
    "Foundation Models",
    "Diffusion Models",
    "AI in Healthcare",
    "AI in Education",
    "Military AI Applications",
    "Human-AI Collaboration"
]

# Count the frequency of these topics in arxiv paper titles
arxiv_papers = []
with open("arxiv_data.txt", "w") as f:
    f.write("Recent AI Research Papers from arXiv:\n\n")
    
    # Parse the arXiv data
    arxiv_data = """
    Stop Summation: Min-Form Credit Assignment Is All Process Reward Model Needs for Reasoning
    Leveraging Language Models for Automated Patient Record Linkage
    FlowReasoner: Reinforcing Query-Level Meta-Agents
    SuoiAI: Building a Dataset for Aquatic Invertebrates in Vietnam
    A Self-Improving Coding Agent
    Position: Bayesian Statistics Facilitates Stakeholder Participation in Evaluation of Generative AI
    Synergistic Weak-Strong Collaboration by Aligning Preferences
    Behavioral Universe Network (BUN): A Behavioral Information-Based Framework for Complex Systems
    Contemplative Wisdom for Superalignment
    Mitigating Degree Bias in Graph Representation Learning with Learnable Structural Augmentation
    Text-to-Decision Agent: Learning Generalist Policies from Natural Language Supervision
    Evaluating Code Generation of LLMs in Advanced Computer Science Problems
    Generative Semantic Communications: Principles and Practices
    EducationQ: Evaluating LLMs' Teaching Capabilities Through Multi-Agent Dialogue Framework
    OTC: Optimal Tool Calls via Reinforcement Learning
    AlignRAG: An Adaptable Framework for Resolving Misalignments in Retrieval-Aware Reasoning of RAG
    Establishing Reliability Metrics for Reward Models in Large Language Models
    DONOD: Robust and Generalizable Instruction Fine-Tuning for LLMs via Model-Intrinsic Dataset Pruning
    PLANET: A Collection of Benchmarks for Evaluating LLMs' Planning Capabilities
    AI with Emotions: Exploring Emotional Expressions in Large Language Models
    A Framework for Benchmarking and Aligning Task-Planning Safety in LLM-Based Embodied Agents
    UFO2: The Desktop AgentOS
    Toward the Axiomatization of Intelligence: Structure, Time, and Existence
    LLM-Enabled In-Context Learning for Data Collection Scheduling in UAV-assisted Sensor Networks
    Learning from Reasoning Failures via Synthetic Data Generation
    Meta-Thinking in LLMs via Multi-Agent Reinforcement Learning: A Survey
    Seeing Through Risk: A Symbolic Approximation of Prospect Theory
    The Geometry of Self-Verification in a Task-Specific Reasoning Model
    Mathematical Programming Models for Exact and Interpretable Formulation of Neural Networks
    Time Up! An Empirical Study of LLM Reasoning Ability Under Output Length Constraint
    FAIRGAME: a Framework for AI Agents Bias Recognition using Game Theory
    RadioDiff-Inverse: Diffusion Enhanced Bayesian Inverse Estimation for ISAC Radio Map Construction
    CHAINSFORMER: Numerical Reasoning on Knowledge Graphs from a Chain Perspective
    ProtPainter: Draw or Drag Protein via Topology-guided Diffusion
    Rethinking Traffic Flow Forecasting: From Transition to Generatation
    A Knowledge-Informed Deep Learning Paradigm for Generalizable and Stability-Optimized Car-Following Models
    InfiGUI-R1: Advancing Multimodal GUI Agents from Reactive Actors to Deliberative Reasoners
    Assessing AI-Generated Questions' Alignment with Cognitive Frameworks in Educational Assessment
    Pets: General Pattern Assisted Architecture For Time Series Analysis
    AI Idea Bench 2025: AI Research Idea Generation Benchmark
    Direct Advantage Regression: Aligning LLMs with Online AI Reward
    Adaptation Method for Misinformation Identification
    TALES: Text Adventure Learning Environment Suite
    Large Language Model Enhanced Particle Swarm Optimization for Hyperparameter Tuning for Deep Learning Models
    Bayesian Principles Improve Prompt Learning In Vision-Language Models
    CODECRASH: Stress Testing LLM Reasoning under Structural and Semantic Perturbations
    Linking forward-pass dynamics in Transformers and real-time human processing
    Think Deep, Think Fast: Investigating Efficiency of Verifier-free Inference-time-scaling Methods
    Metacognition and Uncertainty Communication in Humans and Large Language Models
    """
    
    # Clean and extract the paper titles
    paper_titles = [title.strip() for title in arxiv_data.strip().split('\n') if title.strip()]
    
    for title in paper_titles:
        arxiv_papers.append(title)
        f.write(f"- {title}\n")

# Count the frequency of key AI topics in the paper titles
topic_counts = {}
for topic in ai_research_topics:
    pattern = re.compile(r'\b' + re.escape(topic.lower().replace('(', '').replace(')', '').replace('-', ' ')) + r'\b', re.IGNORECASE)
    count = sum(1 for paper in arxiv_papers if re.search(pattern, paper.lower()))
    
    # Additional checks for specific terms
    if topic == "Large Language Models (LLMs)":
        count += sum(1 for paper in arxiv_papers if "LLM" in paper or "LLMs" in paper)
    elif topic == "AI Agents":
        count += sum(1 for paper in arxiv_papers if "Agent" in paper or "Agents" in paper)
    elif topic == "Reinforcement Learning":
        count += sum(1 for paper in arxiv_papers if "RL" in paper)
    elif topic == "Natural Language Processing":
        count += sum(1 for paper in arxiv_papers if "NLP" in paper)
    
    topic_counts[topic] = count

# Extract key trends from news articles
ai_news_trends = [
    "AI agents with multiple personalities",
    "OpenAI's new GPT 4.1 models excelling at coding",
    "Open source AI robots",
    "Small language models gaining popularity",
    "Palantir's collaboration with government agencies",
    "AI in immigration surveillance",
    "AI in military applications",
    "China's advancement in AI and robotics",
    "AI ethics and safety concerns",
    "Regulatory approaches to AI",
    "AI hallucination issues",
    "Superintelligence concerns",
    "Open weight AI models",
    "Amazon's AGI lab's work on advanced AI agents",
    "Issues with AI image generators",
]

# Create a summary of AI trends
with open("ai_trends_summary.txt", "w") as f:
    f.write("# Key AI Trends and Developments in 2025\n\n")
    
    f.write("## Major Research Directions\n\n")
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    for topic, count in sorted_topics:
        if count > 0:
            f.write(f"- **{topic}**: {count} recent papers\n")
    
    f.write("\n## Notable Industry Developments\n\n")
    for trend in ai_news_trends:
        f.write(f"- {trend}\n")
    
    f.write("\n## Key AI Advancements\n\n")
    f.write("1. **AI Agents**: Autonomous AI systems capable of performing complex tasks, making decisions, and interacting with their environment are gaining significant traction.\n")
    f.write("2. **Small Language Models (SLMs)**: More efficient, specialized AI models that require fewer computational resources while maintaining good performance for specific tasks.\n")
    f.write("3. **Multimodal AI**: Systems that can process and understand multiple types of data (text, images, audio, etc.) simultaneously.\n")
    f.write("4. **AI Alignment and Safety**: Increasing focus on ensuring AI systems behave according to human values and intentions.\n")
    f.write("5. **Government and Military Applications**: Growing use of AI in surveillance, defense, and government operations.\n")
    
    f.write("\n## Challenges and Concerns\n\n")
    f.write("1. **AI Hallucinations**: AI systems generating false or misleading information remains a significant challenge.\n")
    f.write("2. **Ethics and Regulation**: Questions about how to govern AI development and deployment ethically.\n")
    f.write("3. **Privacy Concerns**: AI systems collecting and potentially misusing personal data.\n")
    f.write("4. **Job Displacement**: Automation of tasks previously performed by humans.\n")
    f.write("5. **Superintelligence Risks**: Theoretical concerns about advanced AI systems surpassing human intelligence.\n")

# Create a text-based visualization of the top research topics
with open("top_ai_topics.txt", "w") as f:
    f.write("Top 10 AI Research Topics in 2025\n")
    f.write("================================\n\n")
    
    top_topics = dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    max_topic_length = max(len(topic) for topic in top_topics.keys())
    max_count = max(top_topics.values())
    
    for topic, count in top_topics.items():
        bar_length = int(50 * count / max_count)
        bar = '#' * bar_length
        f.write(f"{topic.ljust(max_topic_length)} | {bar} ({count})\n")

print("AI research analysis complete. Files generated: ai_trends_summary.txt, top_ai_topics.txt, arxiv_data.txt")