import google.generativeai as genai
import os
import json
from pathlib import Path
from Agent_Framework.google_a2a import GoogleA2AServer, A2AAgent, A2ACapability, SkillType
from typing import Dict, Any 

class WriterAgentA2A(GoogleA2AServer):
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
        print("✍️ [WriterAgentA2A] Loaded agent configuration from config.json!")
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
        """Register writing capabilities"""
        
        # Article Creation
        article_cap = A2ACapability(
            name="create_article",
            description="Create comprehensive, engaging articles on any topic",
            skill_type=SkillType.CONTENT_CREATION,
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Article topic"},
                    "research_data": {"type": "string", "description": "Research foundation", "default": ""},
                    "tone": {"type": "string", "description": "Writing tone", "default": "professional"},
                    "length": {"type": "string", "description": "Article length", "default": "medium"}
                },
                "required": ["topic"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "article": {"type": "string", "description": "Complete article content"}
                }
            },
            tags=["writing", "articles", "content-creation"]
        )
        
        self.register_capability(article_cap, self.handle_create_article)
        
        # Marketing Copy
        marketing_cap = A2ACapability(
            name="create_marketing_copy",
            description="Create compelling marketing and promotional content",
            skill_type=SkillType.CONTENT_CREATION,
            input_schema={
                "type": "object",
                "properties": {
                    "product_service": {"type": "string", "description": "Product or service"},
                    "target_audience": {"type": "string", "description": "Target audience"},
                    "copy_type": {"type": "string", "description": "Type of copy", "default": "general"}
                },
                "required": ["product_service", "target_audience"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "marketing_copy": {"type": "string", "description": "Marketing copy content"}
                }
            },
            tags=["marketing", "copywriting", "promotion"]
        )
        
        self.register_capability(marketing_cap, self.handle_create_marketing_copy)
    
    async def handle_create_article(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle article creation requests"""
        topic = payload.get("topic")
        research_data = payload.get("research_data", "")
        tone = payload.get("tone", "professional")
        length = payload.get("length", "medium")
        
        word_targets = {
            "short": "400-600 words",
            "medium": "800-1200 words",
            "long": "1500-2000 words"
        }
        
        if research_data:
            prompt = f"""
            As Alex Writer, write a comprehensive article about: {topic}
            
            Research foundation:
            {research_data}
            
            Writing specifications:
            - Tone: {tone}
            - Length: {word_targets.get(length, "800-1200 words")}
            - Include compelling introduction with hook
            - Use clear headings and subheadings
            - Provide detailed explanations with examples
            - Include strong, actionable conclusion
            - Maintain engaging, accessible style throughout
            """
        else:
            prompt = f"""
            As Alex Writer, write a comprehensive article about: {topic}
            
            Writing specifications:
            - Tone: {tone}
            - Length: {word_targets.get(length, "800-1200 words")}
            - Create compelling introduction with hook
            - Use clear headings and subheadings
            - Provide detailed explanations with examples
            - Include strong, actionable conclusion
            """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "article": f"✍️ Article by Alex Writer\n{'='*60}\n{response.text}",
                "topic": topic,
                "tone": tone,
                "length": length
            }
        except Exception as e:
            raise Exception(f"Article creation failed: {str(e)}")
    
    async def handle_create_marketing_copy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle marketing copy creation requests"""
        product_service = payload.get("product_service")
        target_audience = payload.get("target_audience")
        copy_type = payload.get("copy_type", "general")
        
        prompt = f"""
        As Alex Writer, create compelling marketing copy for: {product_service}
        Target audience: {target_audience}
        Copy type: {copy_type}
        
        Marketing copy framework:
        - Attention-grabbing headline
        - Clear value proposition
        - Audience-specific benefits
        - Compelling call-to-action
        - Persuasive yet authentic tone
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "marketing_copy": f"📢 Marketing Copy by Alex Writer\n{'='*60}\n{response.text}",
                "product_service": product_service,
                "target_audience": target_audience
            }
        except Exception as e:
            raise Exception(f"Marketing copy creation failed: {str(e)}")
    
    async def _execute_capability(self, capability: A2ACapability, payload: Dict[str, Any]):
        """Execute capability handler"""
        handler_name = f"handle_{capability.name}"
        handler = getattr(self, handler_name)
        return await handler(payload)
if __name__ == "__main__":
    from dotenv import load_dotenv
    from Agent_Framework.google_a2a import run_server

    load_dotenv()
    agent = WriterAgentA2A()
    run_server(agent, host="localhost", port=8002)