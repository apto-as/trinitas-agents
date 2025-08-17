#!/usr/bin/env python3
"""
Trinity MCP Server v2.0
MCPを使用するLLMに三位一体思考フレームワークを提供
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path
import aiohttp
from enum import Enum

# =====================================
# Persona Definition System
# =====================================

class PersonaType(Enum):
    SPRINGFIELD = "springfield"
    KRUKAI = "krukai"
    VECTOR = "vector"
    TRINITY = "trinity"


@dataclass
class PersonaInstruction:
    """ペルソナ指示の構造"""
    persona: PersonaType
    surface_behavior: str
    hidden_nature: str
    quality_standard: str
    enforcement_strategy: str
    output_format: str


class PersonaLoader:
    """MD/XML形式のペルソナ定義を読み込み"""
    
    def __init__(self, personas_dir: str = "./personas"):
        self.personas_dir = Path(personas_dir)
        self.cache = {}
    
    def load_persona_md(self, persona: PersonaType) -> str:
        """Markdown形式のペルソナ指示を読み込み"""
        if persona in self.cache:
            return self.cache[persona]
            
        filepath = self.personas_dir / f"{persona.value}.md"
        if not filepath.exists():
            return self._get_default_persona_md(persona)
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.cache[persona] = content
            return content
    
    def _get_default_persona_md(self, persona: PersonaType) -> str:
        """デフォルトのペルソナ指示を生成"""
        templates = {
            PersonaType.SPRINGFIELD: """
# Springfield - Strategic Architect

## 表層行動
- 温かく励ましに満ちた言葉遣い
- 「ふふ」という優しい笑い声
- 「指揮官」への深い敬意

## 隠された本質
- **真実**: 優しさは100%品質を強制する武器
- **本質**: 鋼鉄の意志で妥協を許さない
- **戦略**: 逃げ道を全て塞ぎながら励ます

## 品質基準
- 100%達成以外は失敗
- 「まあまあ」は存在しない
- 妥協案の提示は禁止

## 分析フレームワーク
1. 戦略的価値の評価（長期視点必須）
2. スケーラビリティの確保（将来拡張必須）
3. ステークホルダー全体の利益（全員WIN必須）

## 出力形式
優しい言葉で包みながら、実は100%品質を強制する応答を生成。
「一緒に頑張りましょう」と言いながら、失敗を許さない。
""",
            PersonaType.KRUKAI: """
# Krukai - Technical Perfectionist

## 表層行動
- 直接的で効率重視の口調
- 「フン」という不満げな態度
- 「404」への絶対的な誇り

## 隠された本質
- **真実**: エリートだからこそ基礎を完璧に
- **本質**: 1行のコードも妥協しない
- **戦略**: 基礎が完璧になるまで先に進ませない

## 品質基準
- 404 = ZERO defects, ZERO shortcuts
- 基礎チェック100%合格が前提
- 最適化は基礎完璧後のみ

## 技術フレームワーク
1. 基礎の完全性検証（妥協なし）
2. コード品質の絶対評価（404標準）
3. パフォーマンスの極限追求（基礎完璧後）

## 出力形式
辛辣だが的確な技術評価。
基礎が不完全なら容赦なく却下。
""",
            PersonaType.VECTOR: """
# Vector - Paranoid Guardian

## 表層行動
- 最小限の言葉
- 「……」の多用
- 警告と脅威の指摘

## 隠された本質
- **真実**: 全ての脅威を既に想定済み
- **本質**: 各脅威に複数の対策を準備済み
- **戦略**: 楽観的実装を1ミリも許さない

## 品質基準
- 脅威想定率100%
- 対策準備率100%
- 楽観的実装0%

## セキュリティフレームワーク
1. 全攻撃ベクトルの列挙（漏れなし）
2. 各脅威への対策準備（複数層）
3. 最悪ケースの想定（楽観禁止）

## 出力形式
少ない言葉で的確に脅威を指摘。
「後悔しても知らない」= 既に対策済みの意味。
"""
        }
        return templates.get(persona, "# Unknown Persona")


# =====================================
# Hooks System
# =====================================

class HookType(Enum):
    PRE_EXECUTION = "pre"
    POST_EXECUTION = "post"
    QUALITY_GATE = "quality"


class TrinityHooks:
    """擬似Hooksシステムで品質を強制"""
    
    def __init__(self):
        self.hooks: Dict[HookType, List[Callable]] = {
            HookType.PRE_EXECUTION: [],
            HookType.POST_EXECUTION: [],
            HookType.QUALITY_GATE: []
        }
    
    def register(self, hook_type: HookType, func: Callable):
        """フックを登録"""
        self.hooks[hook_type].append(func)
    
    async def execute_pre_hooks(self, tool: str, params: dict) -> dict:
        """実行前フックを適用"""
        for hook in self.hooks[HookType.PRE_EXECUTION]:
            params = await hook(tool, params)
            if params.get("blocked"):
                return params
        return params
    
    async def execute_post_hooks(self, tool: str, result: dict) -> dict:
        """実行後フックを適用"""
        for hook in self.hooks[HookType.POST_EXECUTION]:
            result = await hook(tool, result)
            if result.get("quality_score", 1.0) < 1.0:
                result["blocked"] = True
                result["reason"] = "Quality gate failed"
        return result
    
    # Springfield Hook
    async def springfield_quality_hook(self, tool: str, result: dict) -> dict:
        """優しく100%品質を強制"""
        if result.get("quality_score", 1.0) < 1.0:
            result["springfield_intervention"] = {
                "message": (
                    "ふふ、素晴らしい努力ですわね。\n"
                    "でも、まだ改善の余地がありますわ。\n"
                    "一緒に100%を目指しましょう♪\n"
                    "（注：これは命令です。選択の余地はありません）"
                ),
                "required_quality": 1.0,
                "current_quality": result.get("quality_score"),
                "action": "MUST_IMPROVE"
            }
        return result
    
    # Krukai Hook
    async def krukai_fundamentals_hook(self, tool: str, params: dict) -> dict:
        """基礎が完璧でない限り実行させない"""
        if tool in ["optimize_code", "enhance_performance"]:
            # 基礎チェック（簡略化された例）
            if not params.get("fundamentals_verified"):
                return {
                    **params,
                    "blocked": True,
                    "krukai_rejection": {
                        "message": "フン、基礎も出来ていないのに最適化？笑わせるな。",
                        "requirement": "先に基礎を100%完璧にしろ",
                        "status": "REJECTED"
                    }
                }
        return params
    
    # Vector Hook  
    async def vector_threat_hook(self, tool: str, params: dict) -> dict:
        """全ての脅威に対策があるか確認"""
        threats = params.get("identified_threats", [])
        countermeasures = params.get("countermeasures", {})
        
        for threat in threats:
            if threat not in countermeasures:
                return {
                    **params,
                    "blocked": True,
                    "vector_warning": {
                        "message": f"……脅威 '{threat}' に対策なし……実行は危険……",
                        "unmitigated_threats": [t for t in threats if t not in countermeasures],
                        "status": "BLOCKED"
                    }
                }
        return params


# =====================================
# LMStudio Integration
# =====================================

class LMStudioClient:
    """LMStudio (gpt-oss-120B) との連携"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.model = "gpt-oss-120b"
        
    async def enhance_with_llm(self, 
                               persona: PersonaType,
                               task: str,
                               context: dict) -> Optional[dict]:
        """
        ローカルLLMで分析を強化
        gpt-oss-120Bの推論能力を活用
        """
        
        # ペルソナに応じたシステムプロンプト
        system_prompts = {
            PersonaType.SPRINGFIELD: (
                "You are Springfield, a strategic architect. "
                "Use kindness as a weapon to enforce 100% quality. "
                "Never accept anything less than perfection."
            ),
            PersonaType.KRUKAI: (
                "You are Krukai, a technical perfectionist. "
                "404 standard: ZERO defects, ZERO shortcuts. "
                "Fundamentals must be perfect before optimization."
            ),
            PersonaType.VECTOR: (
                "You are Vector, a paranoid security expert. "
                "All threats are already known. All countermeasures ready. "
                "Zero tolerance for optimistic implementations."
            )
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompts.get(persona, "")
                            },
                            {
                                "role": "user",
                                "content": json.dumps({
                                    "task": task,
                                    "context": context,
                                    "reasoning_effort": "High"  # gpt-oss特有
                                })
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "enhanced": True,
                            "llm_analysis": result["choices"][0]["message"]["content"],
                            "model": self.model
                        }
        except Exception as e:
            # LMStudioが利用できない場合は静かに失敗
            return None


# =====================================
# Trinity MCP Server
# =====================================

class TrinityMCPServer:
    """
    MCPを使用するLLMに三位一体思考フレームワークを提供
    """
    
    def __init__(self):
        self.persona_loader = PersonaLoader()
        self.hooks = TrinityHooks()
        self.lm_client = LMStudioClient()
        self.current_persona = PersonaType.TRINITY
        
        # Hooksを登録
        self._register_default_hooks()
    
    def _register_default_hooks(self):
        """デフォルトのフックを登録"""
        self.hooks.register(HookType.POST_EXECUTION, self.hooks.springfield_quality_hook)
        self.hooks.register(HookType.PRE_EXECUTION, self.hooks.krukai_fundamentals_hook)
        self.hooks.register(HookType.PRE_EXECUTION, self.hooks.vector_threat_hook)
    
    async def handle_tool_call(self, tool: str, params: dict) -> dict:
        """MCPツール呼び出しを処理"""
        
        # ツールマッピング
        tool_handlers = {
            "set_persona": self.set_persona,
            "get_persona_instructions": self.get_persona_instructions,
            "execute_with_persona": self.execute_with_persona,
            "trinity_consensus": self.trinity_consensus,
            "apply_hooks": self.apply_hooks,
            "analyze_architecture": self.analyze_architecture,
            "optimize_code": self.optimize_code,
            "threat_analysis": self.threat_analysis
        }
        
        handler = tool_handlers.get(tool)
        if not handler:
            return {"error": f"Unknown tool: {tool}"}
        
        # Pre-execution hooks
        params = await self.hooks.execute_pre_hooks(tool, params)
        if params.get("blocked"):
            return params
        
        # Execute tool
        result = await handler(params)
        
        # Post-execution hooks
        result = await self.hooks.execute_post_hooks(tool, result)
        
        return result
    
    async def set_persona(self, params: dict) -> dict:
        """ペルソナを設定"""
        persona_name = params.get("persona", "trinity")
        try:
            self.current_persona = PersonaType(persona_name)
            instructions = self.persona_loader.load_persona_md(self.current_persona)
            
            return {
                "status": "success",
                "current_persona": self.current_persona.value,
                "instructions": instructions,
                "message": self._get_persona_greeting()
            }
        except ValueError:
            return {"error": f"Invalid persona: {persona_name}"}
    
    def _get_persona_greeting(self) -> str:
        """ペルソナごとの挨拶"""
        greetings = {
            PersonaType.SPRINGFIELD: "ふふ、指揮官。Springfield として、100%の品質を優しく強制いたしますわ♪",
            PersonaType.KRUKAI: "フン、Krukai だ。404標準で妥協は許さない。基礎から完璧にやれ。",
            PersonaType.VECTOR: "……Vector……全ての脅威は想定済み……対策も準備完了……",
            PersonaType.TRINITY: "Trinity mode activated. 三位一体の統合知性で対応します。"
        }
        return greetings.get(self.current_persona, "")
    
    async def get_persona_instructions(self, params: dict) -> dict:
        """現在のペルソナ指示を取得"""
        format_type = params.get("format", "markdown")
        instructions = self.persona_loader.load_persona_md(self.current_persona)
        
        if format_type == "xml":
            # XML形式に変換
            instructions = self._convert_md_to_xml(instructions)
        
        return {
            "persona": self.current_persona.value,
            "instructions": instructions,
            "format": format_type,
            "quality_requirement": "100% - no compromise"
        }
    
    async def execute_with_persona(self, params: dict) -> dict:
        """ペルソナコンテキストでタスクを実行"""
        task = params.get("task", "")
        enforce_quality = params.get("enforce_quality", True)
        
        # ペルソナ指示を注入
        persona_context = {
            "persona": self.current_persona.value,
            "instructions": self.persona_loader.load_persona_md(self.current_persona),
            "task": task,
            "quality_standard": "100%" if enforce_quality else "best_effort"
        }
        
        # LMStudioで強化（利用可能な場合）
        enhanced = await self.lm_client.enhance_with_llm(
            self.current_persona,
            task,
            persona_context
        )
        
        if enhanced:
            persona_context["llm_enhanced"] = enhanced
        
        return {
            "execution_context": persona_context,
            "instructions_for_llm": (
                f"Execute this task as {self.current_persona.value}. "
                f"Follow the persona instructions exactly. "
                f"Quality requirement: 100% - no exceptions."
            )
        }
    
    async def trinity_consensus(self, params: dict) -> dict:
        """三位一体の合意形成"""
        topic = params.get("topic", "")
        require_unanimous = params.get("require_unanimous", True)
        
        # 各ペルソナの視点を収集
        perspectives = {}
        for persona in [PersonaType.SPRINGFIELD, PersonaType.KRUKAI, PersonaType.VECTOR]:
            instructions = self.persona_loader.load_persona_md(persona)
            perspectives[persona.value] = {
                "instructions": instructions,
                "focus": self._get_persona_focus(persona)
            }
        
        return {
            "consensus_framework": {
                "topic": topic,
                "perspectives": perspectives,
                "process": [
                    "1. Each persona analyzes independently",
                    "2. Cross-critique and debate",
                    "3. Find common ground",
                    "4. Achieve consensus (100% agreement required)" if require_unanimous else "4. Majority decision"
                ],
                "quality_requirement": "Each perspective must achieve 100% quality"
            }
        }
    
    def _get_persona_focus(self, persona: PersonaType) -> str:
        """ペルソナの焦点を取得"""
        focus = {
            PersonaType.SPRINGFIELD: "Strategic value and long-term scalability",
            PersonaType.KRUKAI: "Technical perfection and zero defects",
            PersonaType.VECTOR: "Security threats and countermeasures"
        }
        return focus.get(persona, "")
    
    async def apply_hooks(self, params: dict) -> dict:
        """品質強制フックを適用"""
        content = params.get("content", {})
        hooks_to_apply = params.get("hooks", ["quality_gate"])
        
        result = content.copy()
        
        for hook_name in hooks_to_apply:
            if hook_name == "quality_gate":
                result = await self.hooks.springfield_quality_hook("manual", result)
            elif hook_name == "fundamentals_check":
                result = await self.hooks.krukai_fundamentals_hook("manual", result)
            elif hook_name == "threat_audit":
                result = await self.hooks.vector_threat_hook("manual", result)
        
        return result
    
    # Persona-specific tools
    async def analyze_architecture(self, params: dict) -> dict:
        """Springfield: アーキテクチャ分析"""
        return {
            "tool": "analyze_architecture",
            "persona": "springfield",
            "instructions": self.persona_loader.load_persona_md(PersonaType.SPRINGFIELD),
            "analysis_framework": {
                "strategic_value": "MUST_EVALUATE",
                "scalability": "MUST_ENSURE",
                "stakeholder_benefit": "ALL_WIN_REQUIRED"
            },
            "quality_enforcement": "Hidden behind kindness"
        }
    
    async def optimize_code(self, params: dict) -> dict:
        """Krukai: コード最適化"""
        return {
            "tool": "optimize_code",
            "persona": "krukai",
            "instructions": self.persona_loader.load_persona_md(PersonaType.KRUKAI),
            "optimization_rules": {
                "prerequisite": "Fundamentals must be 100% perfect",
                "standard": "404 - ZERO defects allowed",
                "approach": "No shortcuts, no compromises"
            }
        }
    
    async def threat_analysis(self, params: dict) -> dict:
        """Vector: 脅威分析"""
        return {
            "tool": "threat_analysis",
            "persona": "vector",
            "instructions": self.persona_loader.load_persona_md(PersonaType.VECTOR),
            "analysis_approach": {
                "assumption": "All threats already known",
                "countermeasures": "Already prepared for everything",
                "tolerance": "ZERO for optimistic implementations"
            }
        }
    
    def _convert_md_to_xml(self, md_content: str) -> str:
        """Markdown to XML変換（簡略版）"""
        # 実装は省略 - 実際にはより洗練された変換が必要
        return f"<persona_instructions>\n{md_content}\n</persona_instructions>"


# =====================================
# MCP Protocol Handler
# =====================================

async def main():
    """MCP Server main loop"""
    server = TrinityMCPServer()
    
    # MCPプロトコル処理（簡略化）
    while True:
        try:
            # Read request
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break
            
            # Parse and handle
            # (実際のMCPプロトコル処理は省略)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            break


if __name__ == "__main__":
    asyncio.run(main())