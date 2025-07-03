import google.generativeai as genai
import os
import json
from pathlib import Path
from Agent_Framework.google_a2a import GoogleA2AServer, A2AAgent, A2ACapability, SkillType
from typing import Dict, Any 

class ResearchAgentA2A(GoogleA2AServer):
    def __init__(self):
        # Initialize Google Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load agent configuration from config.json
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
        agent_config = config["agent"]
        
        # Logging configuration load
        print("🔬 [ResearchAgentA2A] Loaded agent configuration from config.json!")
        print(f"🔧 Agent ID: {agent_config['agent_id']}")
        print(f"👤 Name: {agent_config['name']}")
        print(f"📄 Description: {agent_config['description']}")
        print(f"🌐 Endpoint: {agent_config['endpoint']}")
        
        # Define agent using configuration file (no hardcoding)
        agent = A2AAgent(
            agent_id=agent_config["agent_id"],
            name=agent_config["name"],
            description=agent_config["description"],
            version=agent_config["version"],
            endpoint=agent_config["endpoint"],
            supported_protocols=agent_config.get("supported_protocols", ["google-a2a-v1"]),
            metadata=agent_config.get("metadata", {})
        )
        
        super().__init__(agent)
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register research capabilities"""
        
        # Comprehensive Research
        research_cap = A2ACapability(
            name="comprehensive_research",
            description="Conduct thorough research on any topic with structured analysis",
            skill_type=SkillType.RESEARCH,
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                    "focus_areas": {"type": "string", "description": "Specific focus areas", "default": "general"}
                },
                "required": ["topic"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "research_report": {"type": "string", "description": "Comprehensive research report"}
                }
            },
            examples=[
                {"input": {"topic": "AI in healthcare"}, "output": {"research_report": "..."}}
            ],
            tags=["research", "analysis", "comprehensive"]
        )
        
        self.register_capability(research_cap, self.handle_comprehensive_research)
        
        # Trend Analysis
        trend_cap = A2ACapability(
            name="trend_analysis",
            description="Analyze current trends and developments in specific domains",
            skill_type=SkillType.ANALYSIS,
            input_schema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Domain to analyze"},
                    "time_frame": {"type": "string", "description": "Analysis time frame", "default": "current"}
                },
                "required": ["domain"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "trend_report": {"type": "string", "description": "Trend analysis report"}
                }
            },
            tags=["trends", "analysis", "market-research"]
        )
        
        self.register_capability(trend_cap, self.handle_trend_analysis)

        # Structure/Clean Research Capability
        structure_cap = A2ACapability(
            name="structure_research",
            description="Structure or clean user-provided research content for downstream use",
            skill_type=SkillType.RESEARCH,
            input_schema={
                "type": "object",
                "properties": {
                    "raw_research": {"type": "string", "description": "Raw research content to structure/clean"}
                },
                "required": ["raw_research"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "structured_research": {"type": "string", "description": "Structured/cleaned research content"}
                }
            },
            tags=["structure", "clean", "research"]
        )
        self.register_capability(structure_cap, self.handle_structure_research)
    
    async def handle_comprehensive_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive research requests"""
        topic = payload.get("topic")
        focus_areas = payload.get("focus_areas", "general")
        
        prompt = f"""
        As Dr. Research, conduct comprehensive research on: {topic}
        Focus areas: {focus_areas}

        Research Framework:
        1. Key concepts and definitions
        2. Current trends and developments  
        3. Important statistics and data points
        4. Main challenges and opportunities
        5. Expert opinions and viewpoints
        6. Recent developments and innovations
        7. Future outlook and predictions

        Provide structured, evidence-based research with actionable insights.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "research_report": f" Research Report by Dr. Research\n{'='*60}\n{response.text}",
                "topic": topic,
                "focus_areas": focus_areas
            }
        except Exception as e:
            raise Exception(f"Research generation failed: {str(e)}")
    
    async def handle_trend_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trend analysis requests"""
        domain = payload.get("domain")
        time_frame = payload.get("time_frame", "current")
        
        prompt = f"""
        As Dr. Research, analyze current trends in: {domain}
        Time frame: {time_frame}

        Trend Analysis Framework:
        1. Emerging trends and patterns
        2. Market dynamics and drivers
        3. Key players and innovations
        4. Growth statistics and projections
        5. Disruption factors
        6. Future implications

        Provide data-driven trend analysis with supporting evidence.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "trend_report": f" Trend Analysis by Dr. Research\n{'='*60}\n{response.text}",
                "domain": domain,
                "time_frame": time_frame
            }
        except Exception as e:
            raise Exception(f"Trend analysis failed: {str(e)}")
    
    async def handle_structure_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle structuring/cleaning user-provided research content"""
        raw = payload.get("raw_research", "")
        # Placeholder: just wrap the input
        structured = f"[Structured Research]\n{raw.strip()}"
        return {"structured_research": structured}
    
    async def _execute_capability(self, capability: A2ACapability, payload: Dict[str, Any]):
        """Execute capability handler"""
        handler_name = f"handle_{capability.name}"
        handler = getattr(self, handler_name)
        return await handler(payload)
if __name__ == "__main__":
    from dotenv import load_dotenv
    from Agent_Framework.google_a2a import run_server  # Ensure this is the same run_server from your google_a2a.py

    load_dotenv()
    agent = ResearchAgentA2A()
    run_server(agent, host="0.0.0.0", port=8001)