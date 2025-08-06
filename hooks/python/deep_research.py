#!/usr/bin/env python3
"""
deep_research.py - 深層研究エンジン
段階的で包括的な研究を実行する
"""

import json
import sys
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from async_mcp_client import AsyncMCPClient, MCPRequest

class ResearchStrategy(Enum):
    """研究戦略"""
    BREADTH_FIRST = "breadth_first"    # 幅優先探索
    DEPTH_FIRST = "depth_first"        # 深さ優先探索
    ITERATIVE = "iterative"            # 反復的深化
    HYBRID = "hybrid"                  # ハイブリッド

class InformationQuality(Enum):
    """情報品質レベル"""
    PRIMARY = "primary"          # 一次情報源
    SECONDARY = "secondary"      # 二次情報源
    TERTIARY = "tertiary"       # 三次情報源
    UNVERIFIED = "unverified"   # 未検証

@dataclass
class ResearchQuery:
    """研究クエリ"""
    query_id: str
    question: str
    context: Dict[str, Any]
    priority: int = 5
    max_depth: int = 3
    strategy: ResearchStrategy = ResearchStrategy.HYBRID

@dataclass 
class ResearchNode:
    """研究ツリーのノード"""
    node_id: str
    query: ResearchQuery
    depth: int
    parent_id: Optional[str]
    children: List[str] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, exploring, completed, failed
    quality_score: float = 0.0

@dataclass
class ResearchPath:
    """研究パス（ルートから葉までの経路）"""
    path_id: str
    nodes: List[str]
    total_quality: float
    insights: List[str]
    dead_end: bool = False

class DeepResearchEngine:
    """深層研究エンジン"""
    
    def __init__(self):
        self.research_trees: Dict[str, Dict[str, ResearchNode]] = {}
        self.research_paths: Dict[str, ResearchPath] = {}
        self.quality_thresholds = {
            InformationQuality.PRIMARY: 0.9,
            InformationQuality.SECONDARY: 0.7,
            InformationQuality.TERTIARY: 0.5,
            InformationQuality.UNVERIFIED: 0.3
        }
        
        # 研究戦略の実装
        self.strategies = {
            ResearchStrategy.BREADTH_FIRST: self._breadth_first_strategy,
            ResearchStrategy.DEPTH_FIRST: self._depth_first_strategy,
            ResearchStrategy.ITERATIVE: self._iterative_strategy,
            ResearchStrategy.HYBRID: self._hybrid_strategy
        }
        
        # MCPサーバー優先順位
        self.server_priorities = {
            "arxiv": 1,      # 学術論文
            "gemini": 2,     # 高度な分析
            "context7": 3,   # 技術文書
            "web_search": 4  # 一般的な情報
        }
    
    async def conduct_deep_research(self, initial_query: ResearchQuery) -> Dict[str, Any]:
        """深層研究を実施"""
        tree_id = f"tree_{initial_query.query_id}_{time.time()}"
        self.research_trees[tree_id] = {}
        
        # ルートノードを作成
        root_node = ResearchNode(
            node_id=f"node_root_{tree_id}",
            query=initial_query,
            depth=0,
            parent_id=None
        )
        self.research_trees[tree_id][root_node.node_id] = root_node
        
        # 選択された戦略で研究を実行
        strategy_func = self.strategies.get(
            initial_query.strategy, 
            self._hybrid_strategy
        )
        
        # 研究を実行
        await strategy_func(tree_id, root_node)
        
        # 結果を集約
        result = await self._aggregate_research_results(tree_id)
        
        return result
    
    async def _breadth_first_strategy(self, tree_id: str, root_node: ResearchNode):
        """幅優先探索戦略"""
        queue = [root_node.node_id]
        
        while queue:
            current_id = queue.pop(0)
            current_node = self.research_trees[tree_id][current_id]
            
            if current_node.depth >= current_node.query.max_depth:
                continue
            
            # 現在のノードを探索
            await self._explore_node(tree_id, current_node)
            
            # 子ノードを生成
            child_queries = await self._generate_child_queries(current_node)
            
            for child_query in child_queries:
                child_node = await self._create_child_node(
                    tree_id, current_node, child_query
                )
                queue.append(child_node.node_id)
    
    async def _depth_first_strategy(self, tree_id: str, root_node: ResearchNode):
        """深さ優先探索戦略"""
        async def dfs(node_id: str):
            node = self.research_trees[tree_id][node_id]
            
            if node.depth >= node.query.max_depth:
                return
            
            # ノードを探索
            await self._explore_node(tree_id, node)
            
            # 最も有望な子ノードを選択して深く探索
            child_queries = await self._generate_child_queries(node)
            
            if child_queries:
                # 優先度が最も高いクエリを選択
                best_query = max(child_queries, key=lambda q: q.priority)
                child_node = await self._create_child_node(
                    tree_id, node, best_query
                )
                await dfs(child_node.node_id)
        
        await dfs(root_node.node_id)
    
    async def _iterative_strategy(self, tree_id: str, root_node: ResearchNode):
        """反復的深化戦略"""
        max_depth = root_node.query.max_depth
        
        for current_depth in range(1, max_depth + 1):
            # 各深さレベルで探索
            await self._explore_at_depth(tree_id, root_node, current_depth)
            
            # 品質をチェックして早期終了を判断
            quality = await self._assess_tree_quality(tree_id)
            if quality > 0.85:  # 十分な品質に達した
                break
    
    async def _hybrid_strategy(self, tree_id: str, root_node: ResearchNode):
        """ハイブリッド戦略（幅優先と深さ優先の組み合わせ）"""
        # レベル1: 幅優先で概要を把握
        await self._explore_node(tree_id, root_node)
        level1_queries = await self._generate_child_queries(root_node)
        
        level1_nodes = []
        for query in level1_queries[:5]:  # 上位5つ
            child_node = await self._create_child_node(tree_id, root_node, query)
            await self._explore_node(tree_id, child_node)
            level1_nodes.append(child_node)
        
        # レベル2以降: 有望なパスを深く探索
        promising_nodes = sorted(
            level1_nodes, 
            key=lambda n: n.quality_score, 
            reverse=True
        )[:3]  # 上位3つ
        
        for node in promising_nodes:
            if node.depth < node.query.max_depth:
                await self._depth_first_strategy(tree_id, node)
    
    async def _explore_node(self, tree_id: str, node: ResearchNode):
        """ノードを探索"""
        node.status = "exploring"
        
        # MCPサーバーから情報を収集
        findings = await self._gather_information(node.query)
        node.findings = findings
        
        # 品質スコアを計算
        node.quality_score = self._calculate_quality_score(findings)
        
        node.status = "completed"
    
    async def _gather_information(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """情報を収集"""
        findings = []
        
        async with AsyncMCPClient() as client:
            requests = []
            
            # 各MCPサーバーにリクエストを作成
            # ArXiv検索
            if "academic" in query.context.get("domains", []):
                requests.append(MCPRequest(
                    request_id=f"deep_arxiv_{query.query_id}_{time.time()}",
                    server="arxiv",
                    method="search",
                    params={
                        "query": query.question,
                        "max_results": 10
                    }
                ))
            
            # Gemini分析
            requests.append(MCPRequest(
                request_id=f"deep_gemini_{query.query_id}_{time.time()}",
                server="gemini",
                method="analyze",
                params={
                    "prompt": f"Deep analysis: {query.question}",
                    "context": query.context
                }
            ))
            
            # Context7ドキュメント
            if "technical" in query.context.get("domains", []):
                requests.append(MCPRequest(
                    request_id=f"deep_context7_{query.query_id}_{time.time()}",
                    server="context7",
                    method="search",
                    params={"query": query.question}
                ))
            
            # Web検索
            requests.append(MCPRequest(
                request_id=f"deep_web_{query.query_id}_{time.time()}",
                server="web_search",
                method="search",
                params={
                    "query": query.question,
                    "max_results": 5
                }
            ))
            
            # 並列実行
            responses = await client.send_requests_parallel(requests)
            
            # 結果を処理
            for response in responses:
                if response.data:
                    quality = self._assess_information_quality(
                        response.server, response.data
                    )
                    
                    findings.append({
                        "source": response.server,
                        "data": response.data,
                        "quality": quality.value,
                        "quality_score": self.quality_thresholds[quality],
                        "timestamp": time.time(),
                        "cached": response.cached
                    })
        
        return findings
    
    async def _generate_child_queries(self, parent_node: ResearchNode) -> List[ResearchQuery]:
        """子クエリを生成"""
        child_queries = []
        
        # 親ノードの発見から新しい質問を生成
        for finding in parent_node.findings:
            # 各発見から派生する質問を生成
            derived_questions = self._derive_questions(
                parent_node.query.question,
                finding
            )
            
            for question in derived_questions[:3]:  # 各発見から最大3つ
                child_query = ResearchQuery(
                    query_id=f"q_{parent_node.node_id}_{len(child_queries)}",
                    question=question,
                    context={
                        **parent_node.query.context,
                        "parent_question": parent_node.query.question,
                        "depth": parent_node.depth + 1
                    },
                    priority=self._calculate_query_priority(question, finding),
                    max_depth=parent_node.query.max_depth,
                    strategy=parent_node.query.strategy
                )
                child_queries.append(child_query)
        
        # 優先度でソート
        child_queries.sort(key=lambda q: q.priority, reverse=True)
        
        return child_queries[:10]  # 最大10個
    
    async def _create_child_node(self, tree_id: str, parent_node: ResearchNode,
                               query: ResearchQuery) -> ResearchNode:
        """子ノードを作成"""
        child_node = ResearchNode(
            node_id=f"node_{query.query_id}_{time.time()}",
            query=query,
            depth=parent_node.depth + 1,
            parent_id=parent_node.node_id
        )
        
        # ツリーに追加
        self.research_trees[tree_id][child_node.node_id] = child_node
        parent_node.children.append(child_node.node_id)
        
        return child_node
    
    async def _explore_at_depth(self, tree_id: str, root_node: ResearchNode, 
                              target_depth: int):
        """特定の深さで探索"""
        nodes_at_depth = self._get_nodes_at_depth(tree_id, target_depth - 1)
        
        for node in nodes_at_depth:
            if node.status == "completed" and node.depth < node.query.max_depth:
                child_queries = await self._generate_child_queries(node)
                
                for query in child_queries[:3]:  # 各ノードから最大3つ
                    child_node = await self._create_child_node(tree_id, node, query)
                    await self._explore_node(tree_id, child_node)
    
    async def _assess_tree_quality(self, tree_id: str) -> float:
        """研究ツリーの品質を評価"""
        tree = self.research_trees[tree_id]
        
        if not tree:
            return 0.0
        
        # 各ノードの品質スコアの加重平均
        total_score = 0.0
        total_weight = 0.0
        
        for node in tree.values():
            if node.status == "completed":
                # 深さに応じて重みを調整（深いほど重要）
                weight = 1.0 + (node.depth * 0.2)
                total_score += node.quality_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _aggregate_research_results(self, tree_id: str) -> Dict[str, Any]:
        """研究結果を集約"""
        tree = self.research_trees[tree_id]
        
        # パスを抽出
        paths = self._extract_research_paths(tree_id)
        
        # 最良のパスを選択
        best_paths = sorted(
            paths.values(), 
            key=lambda p: p.total_quality, 
            reverse=True
        )[:5]
        
        # 全体の発見を集約
        all_findings = []
        key_insights = []
        
        for node in tree.values():
            if node.status == "completed":
                all_findings.extend(node.findings)
                
                # 高品質な発見から洞察を抽出
                high_quality_findings = [
                    f for f in node.findings 
                    if f.get("quality_score", 0) > 0.7
                ]
                
                for finding in high_quality_findings:
                    insight = self._extract_insight(node.query.question, finding)
                    if insight:
                        key_insights.append(insight)
        
        # 研究マップを生成
        research_map = self._generate_research_map(tree_id)
        
        return {
            "tree_id": tree_id,
            "total_nodes_explored": len([n for n in tree.values() if n.status == "completed"]),
            "max_depth_reached": max(n.depth for n in tree.values()),
            "total_findings": len(all_findings),
            "high_quality_findings": len([f for f in all_findings if f.get("quality_score", 0) > 0.7]),
            "key_insights": key_insights[:20],  # 上位20個
            "best_research_paths": [
                {
                    "path": [tree[nid].query.question for nid in path.nodes],
                    "quality": path.total_quality,
                    "insights": path.insights
                }
                for path in best_paths
            ],
            "research_map": research_map,
            "quality_score": await self._assess_tree_quality(tree_id)
        }
    
    def _assess_information_quality(self, server: str, data: Any) -> InformationQuality:
        """情報の品質を評価"""
        # サーバーと内容に基づいて品質を判定
        if server == "arxiv":
            return InformationQuality.PRIMARY  # 学術論文は一次情報源
        elif server == "gemini":
            return InformationQuality.SECONDARY  # 分析結果は二次情報源
        elif server == "context7":
            return InformationQuality.SECONDARY  # 技術文書は二次情報源
        elif server == "web_search":
            # Web検索結果は内容により判定
            if isinstance(data, dict) and data.get("scholarly", False):
                return InformationQuality.SECONDARY
            else:
                return InformationQuality.TERTIARY
        else:
            return InformationQuality.UNVERIFIED
    
    def _derive_questions(self, parent_question: str, finding: Dict[str, Any]) -> List[str]:
        """発見から新しい質問を導出"""
        questions = []
        
        # 発見の内容に基づいて質問を生成
        if "gaps" in str(finding.get("data", "")):
            questions.append(f"What are the specific gaps in {parent_question}?")
        
        if "implementation" in str(finding.get("data", "")):
            questions.append(f"How to implement the findings from {parent_question}?")
        
        if "alternative" in str(finding.get("data", "")):
            questions.append(f"What are alternative approaches to {parent_question}?")
        
        # デフォルトの深掘り質問
        questions.extend([
            f"What are the implications of {parent_question}?",
            f"What are the limitations of current approaches to {parent_question}?",
            f"What future research is needed for {parent_question}?"
        ])
        
        return questions[:5]  # 最大5つ
    
    def _calculate_query_priority(self, question: str, parent_finding: Dict[str, Any]) -> int:
        """クエリの優先度を計算"""
        priority = 5  # デフォルト
        
        # 親の発見の品質に基づいて調整
        parent_quality = parent_finding.get("quality_score", 0.5)
        priority += int(parent_quality * 3)
        
        # 質問のタイプに基づいて調整
        if "implement" in question.lower():
            priority += 2  # 実装関連は高優先度
        elif "limitation" in question.lower():
            priority += 1  # 制限事項も重要
        
        return min(10, max(1, priority))  # 1-10の範囲
    
    def _calculate_quality_score(self, findings: List[Dict[str, Any]]) -> float:
        """発見の品質スコアを計算"""
        if not findings:
            return 0.0
        
        # 各発見の品質スコアの加重平均
        total_score = 0.0
        total_weight = 0.0
        
        for finding in findings:
            score = finding.get("quality_score", 0.5)
            # サーバーの優先度を重みとして使用
            weight = 1.0 / self.server_priorities.get(finding.get("source", ""), 5)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _get_nodes_at_depth(self, tree_id: str, depth: int) -> List[ResearchNode]:
        """特定の深さのノードを取得"""
        tree = self.research_trees[tree_id]
        return [node for node in tree.values() if node.depth == depth]
    
    def _extract_research_paths(self, tree_id: str) -> Dict[str, ResearchPath]:
        """研究パスを抽出"""
        tree = self.research_trees[tree_id]
        paths = {}
        
        # リーフノードから逆方向にパスを構築
        leaf_nodes = [n for n in tree.values() if not n.children]
        
        for leaf in leaf_nodes:
            path_nodes = []
            current = leaf
            
            # ルートまで遡る
            while current:
                path_nodes.insert(0, current.node_id)
                current = tree.get(current.parent_id) if current.parent_id else None
            
            # パスの品質を計算
            path_quality = sum(tree[nid].quality_score for nid in path_nodes) / len(path_nodes)
            
            # パスから洞察を抽出
            path_insights = []
            for node_id in path_nodes:
                node = tree[node_id]
                for finding in node.findings:
                    if finding.get("quality_score", 0) > 0.7:
                        insight = self._extract_insight(node.query.question, finding)
                        if insight:
                            path_insights.append(insight)
            
            path = ResearchPath(
                path_id=f"path_{leaf.node_id}",
                nodes=path_nodes,
                total_quality=path_quality,
                insights=path_insights[:10]  # 最大10個
            )
            
            paths[path.path_id] = path
        
        return paths
    
    def _extract_insight(self, question: str, finding: Dict[str, Any]) -> Optional[str]:
        """発見から洞察を抽出"""
        # 簡易実装
        if finding.get("quality_score", 0) > 0.7:
            source = finding.get("source", "unknown")
            return f"[{source}] Key finding for '{question}'"
        return None
    
    def _generate_research_map(self, tree_id: str) -> Dict[str, Any]:
        """研究マップを生成"""
        tree = self.research_trees[tree_id]
        
        # ツリー構造を表現
        def build_node_map(node_id: str) -> Dict[str, Any]:
            node = tree[node_id]
            return {
                "question": node.query.question,
                "depth": node.depth,
                "quality": node.quality_score,
                "findings_count": len(node.findings),
                "children": [build_node_map(child_id) for child_id in node.children]
            }
        
        # ルートノードを見つける
        root_nodes = [n for n in tree.values() if n.parent_id is None]
        
        if root_nodes:
            return build_node_map(root_nodes[0].node_id)
        else:
            return {}

async def execute_deep_research(topic: str, questions: List[str], 
                              domains: List[str], max_depth: int = 3) -> Dict[str, Any]:
    """深層研究を実行（外部インターフェース）"""
    engine = DeepResearchEngine()
    
    # 初期クエリを作成
    initial_query = ResearchQuery(
        query_id=f"main_{int(time.time())}",
        question=topic,
        context={
            "domains": domains,
            "sub_questions": questions
        },
        priority=10,
        max_depth=max_depth,
        strategy=ResearchStrategy.HYBRID
    )
    
    # 研究を実行
    result = await engine.conduct_deep_research(initial_query)
    
    return result

def main():
    """Claude Code Hook として実行"""
    input_data = json.loads(sys.stdin.read())
    
    action = input_data.get("action", "deep_research")
    
    try:
        if action == "deep_research":
            # 深層研究を実行
            topic = input_data.get("topic", "")
            questions = input_data.get("questions", [])
            domains = input_data.get("domains", [])
            max_depth = input_data.get("max_depth", 3)
            
            if not topic:
                raise ValueError("Research topic is required")
            
            # 非同期で実行
            result = asyncio.run(
                execute_deep_research(topic, questions, domains, max_depth)
            )
            
            response = {
                "decision": "approve",
                "metadata": {
                    "deep_research_result": result,
                    "message": f"Deep research completed: {result['total_nodes_explored']} nodes explored"
                }
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    except Exception as e:
        response = {
            "decision": "reject",
            "message": f"Deep research error: {str(e)}",
            "metadata": {
                "error": str(e)
            }
        }
    
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # テストモード
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_input = {
            "action": "deep_research",
            "topic": "Distributed consensus algorithms",
            "questions": [
                "What are the main approaches?",
                "How do they handle network partitions?",
                "What are the trade-offs?"
            ],
            "domains": ["distributed_systems", "computer_science"],
            "max_depth": 2
        }
        
        import io
        sys.stdin = io.StringIO(json.dumps(test_input))
        main()
    else:
        main()