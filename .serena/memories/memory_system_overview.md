# Memory System Overview

This document provides an overview of the new Memory System introduced in Trinitas v3.5.

## Purpose

The Memory System is a major new feature designed to give the Trinitas agents the ability to learn and remember information from their interactions. This allows them to maintain context across sessions, recall past solutions, and improve their performance over time.

## Architecture

The system is based on a cognitive architecture that mimics human memory. It consists of four main types of memory:

1.  **Working Memory (短期記憶):** Holds information related to the current task. It's short-term and has a limited capacity.
2.  **Episodic Memory (エピソード記憶):** Stores the history of past events and interactions, like a personal diary.
3.  **Semantic Memory (意味記憶):** A long-term knowledge base that stores facts, concepts, and technical specifications.
4.  **Procedural Memory (手続き記憶):** Remembers how to do things, such as best practices, optimization techniques, and problem-solving patterns.

A central **Memory Controller** manages the flow of information between these different memory types, including processes for memory consolidation (moving information from short-term to long-term memory) and forgetting.

## Persona-Specific Memory

Each of the five personas has its own dedicated memory system with different priorities and retention policies tailored to its specific role. For example:

*   **Athena** prioritizes semantic and procedural memory to remember architectural patterns and best practices.
*   **Artemis** focuses on procedural memory for optimization techniques.
*   **Hestia** emphasizes episodic and semantic memory to recall security incidents and vulnerabilities.

## MCP Tools

The Memory System is exposed through a set of MCP tools, which allow users and other systems to interact with the agents' memories. The core tools include:

*   `trinitas_remember`: To store information in an agent's memory.
*   `trinitas_recall`: To retrieve information from an agent's memory.
*   `trinitas_share_memory`: To share memories between different personas.

This new Memory System transforms the Trinitas agents from stateless tools into a dynamic and learning system that can evolve and improve with each interaction.
