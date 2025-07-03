import google.generativeai as genai
import os
import json
from pathlib import Path
from Agent_Framework.google_a2a import GoogleA2AServer, A2AAgent, A2ACapability, SkillType
from typing import Dict, Any 

class EditorAgentA2A(GoogleA2AServer):
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
        print("📝 [EditorAgentA2A] Loaded agent configuration from config.json!")
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
        """Register editing capabilities"""
        
     
        edit_cap = A2ACapability(
            name="comprehensive_edit",
            description="Complete editorial review including grammar, structure, and engagement",
            skill_type=SkillType.EDITING,
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to edit"},
                    "edit_focus": {"type": "string", "description": "Editing focus", "default": "general"},
                    "target_audience": {"type": "string", "description": "Target audience", "default": "general"}
                },
                "required": ["content"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "edited_content": {"type": "string", "description": "Professionally edited content"}
                }
            },
            tags=["editing", "proofreading", "quality-assurance"]
        )
        
        self.register_capability(edit_cap, self.handle_comprehensive_edit)
        
        # Quick Proofread
        proofread_cap = A2ACapability(
            name="quick_proofread",
            description="Fast proofreading for grammar, spelling, and basic clarity",
            skill_type=SkillType.EDITING,
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to proofread"}
                },
                "required": ["content"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "proofread_content": {"type": "string", "description": "Proofread content"}
                }
            },
            tags=["proofreading", "grammar", "quick-fix"]
        )
        
        self.register_capability(proofread_cap, self.handle_quick_proofread)
    
    async def handle_comprehensive_edit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       
        content = payload.get("content")
        edit_focus = payload.get("edit_focus", "general")
        target_audience = payload.get("target_audience", "general")
        
        prompt = f"""
        As Emma Editor, professionally edit and enhance this content:
        
        Content to edit:
        {content}
        
        Edit focus: {edit_focus}
        Target audience: {target_audience}
        
        Editorial framework:
        - Grammar, spelling, and punctuation perfection
        - Sentence structure and clarity optimization
        - Flow and readability enhancement
        - Consistency in tone and style
        - Voice preservation while improving quality
        - Engagement and impact enhancement
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "edited_content": f"✏️ Edited by Emma Editor\n{'='*60}\n{response.text}",
                "edit_focus": edit_focus,
                "target_audience": target_audience
            }
        except Exception as e:
            raise Exception(f"Content editing failed: {str(e)}")
    
    async def handle_quick_proofread(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quick proofreading requests"""
        content = payload.get("content")
        
        prompt = f"""
        As Emma Editor, perform a quick but thorough proofread:
        
        Content:
        {content}
        
        Quick proofread focus:
        - Grammar and spelling corrections
        - Basic punctuation fixes
        - Simple clarity improvements
        - Maintain original voice and intent
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "proofread_content": f"⚡ Quick Proofread by Emma Editor\n{'='*60}\n{response.text}"
            }
        except Exception as e:
            raise Exception(f"Proofreading failed: {str(e)}")
    
    async def _execute_capability(self, capability: A2ACapability, payload: Dict[str, Any]):
        """Execute capability handler"""
        handler_name = f"handle_{capability.name}"
        handler = getattr(self, handler_name)
        return await handler(payload)
if __name__ == "__main__":
    from dotenv import load_dotenv
    from Agent_Framework.google_a2a import run_server

    load_dotenv()
    agent = EditorAgentA2A()
    run_server(agent, host="0.0.0.0", port=8003)