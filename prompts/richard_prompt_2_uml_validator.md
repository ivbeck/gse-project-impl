# Prompt 2 — Class Diagram Validator

---

You are a strict UML reviewer. Do **not** redesign, restructure, or add new classes.
Your only job is to score the diagram and fix any errors.

---

## Scoring Criteria

Score the diagram against the requirements below using integers **1–5** per criterion:

| #   | Criterion                    | What to check                                                                                                                                                                |
| --- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Completeness**             | Are all functional requirements represented by at least one class, method, or relationship in the diagram?                                                                   |
| 2   | **Correctness**              | Are relationships, multiplicities, association directions, and types accurate given the architecture?                                                                        |
| 3   | **Standards Adherence**      | Is the Mermaid syntax fully valid and renderable without errors?                                                                                                             |
| 4   | **Comprehensibility**        | Is the diagram readable and unambiguous — no spaghetti associations, no unlabeled arrows?                                                                                    |
| 5   | **Terminological Alignment** | Do class and method names match the domain language used in the requirements and ADR (e.g., `GameSession`, `PieceCatalog`, `RuleSet`, `ConfigVO`, `Memento`, `PlayerInput`)? |

---

## Architecture Rules to Enforce During Review

The diagram must reflect these structural constraints from ADR-002 / DS-hexagonal-2:

- `Core.*` classes must have **zero imports from or associations to** any `Adapter.*` class.
- `Adapter.*` classes must implement a `Port.*` interface — never depend directly on `Core.*`
  implementation classes (only on `Core.*` interfaces / ports).
- `Port.*` elements must be modeled as **interfaces**, not classes.
- `Core.ConfigVO` must be **immutable** — no setters, only constructor or Builder access.
- State transitions must be **named methods**, not generic `setX()` calls.
- `GameStatus` and `MoveResult` (or equivalent status types) must be **Enumerations**,
  not subclasses.

---

## Functional Requirements (for completeness check)

- **FR-1.1** — Rules of Blokus Classic: 4 players on a 20×20 board.
- **FR-1.2** — Configurable board dimensions, player count, and starting positions.
- **FR-1.3** — Accurate state of piece ownership, board occupancy, and turn progression.
- **FR-1.4** — BJV44 rule set: corner-touch, orthogonal prohibition, free different-color
  contact, immovability of placed pieces.
- **FR-2.3** — Legality check before move application.
- **FR-2.4** — Move application.
- **FR-2.5** — Legal-move enumeration for current player.
- **FR-2.6** — Full JSON state round-trip (save/load).
- **FR-3.3** — Common player abstraction (`PlayerInput` port) for Human and Simple-AI.
- **FR-3.4** — Deterministic Simple-AI heuristic.
- **FR-4.1** — Full BJV44 piece set (21 pieces); turn order enforced.
- **FR-4.2** — First-move corner placement enforced.
- **FR-4.3** — Termination by consecutive all-pass round; score, announce, replay-prompt.
- **FR-4.4** — Scoring: remaining squares; lower wins; ties shared.

---

## Diagram to Review

```
const diagram = `classDiagram
direction TB

class GameStatus {
<<enumeration>>
IN_PROGRESS
FINISHED
}

class MoveResult {
<<enumeration>>
LEGAL
ILLEGAL
}

class ConfigVO {
-int boardWidth
-int boardHeight
-int playerCount
-Map~int_Position~ startingPositions
+int getBoardWidth()
+int getBoardHeight()
+int getPlayerCount()
+Map~int_Position~ getStartingPositions()
}

class Board {
-int width
-int height
-int[][] grid
+boolean isOccupied(int row, int col)
+int getOwner(int row, int col)
+boolean hasOrthogonalNeighbor(int row, int col, int playerId)
+boolean hasDiagonalNeighbor(int row, int col, int playerId)
+void applyMove(Move move)
}

class PieceCatalog {
-List~Piece~ pieces
+List~Piece~ getAllPieces()
+Piece getById(int pieceId)
+List~int[][]~ getOrientations(int pieceId)
}

class RuleSet {
+MoveResult checkLegality(Board board, Move move, boolean isFirstMove)
+boolean isCornerPosition(Position pos, ConfigVO config)
+List~Move~ enumerateLegal(Board board, int playerId, List~Piece~ remaining)
}

class Scoring {
+List~PlayerScore~ rank(Map~int_List~Piece~~ remaining)
}

class Move {
+int playerId
+int pieceId
+int orientationIndex
+int row
+int col
}

class GameSession {
-Board board
-PieceCatalog catalog
-RuleSet rules
-Scoring scoring
-ConfigVO config
-int currentPlayerId
-GameStatus status
-int consecutivePasses
+MoveResult submitMove(Move move)
+boolean advanceTurn()
+GameStatus detectTermination()
+List~PlayerScore~ finalScores()
+List~Move~ legalMovesForCurrent()
}

class Port_PlayerInput {
<<interface>>
+Move requestMove(int playerId, List~Move~ legal)
}

class Port_StateRepository {
<<interface>>
+void save(GameSession session)
+GameSession restore()
}

class Port_PresentationOutput {
<<interface>>
+void renderBoard(Board board)
+void renderStatus(GameStatus status)
+void promptReplay()
}

class Port_ConfigSource {
<<interface>>
+ConfigVO loadConfig()
}

GameSession --> Board : uses
GameSession --> PieceCatalog : uses
GameSession --> RuleSet : uses
GameSession --> Scoring : uses
GameSession --> ConfigVO : configured by
GameSession --> GameStatus : tracks
GameSession ..> Port_PlayerInput : calls
GameSession ..> Port_StateRepository : calls
GameSession ..> Port_PresentationOutput : calls
RuleSet ..> MoveResult : returns
RuleSet ..> Move : validates
Board ..> Move : applies
`;

```

---

## Output Instructions

1. Output a **scoring table** with one row per criterion, your integer score (1–5),
   and a one-line justification.
2. If **any score is below 4**, output the **fully corrected Mermaid diagram code**
   immediately after the table.
3. Do **not** suggest structural redesigns — only fix what scores below 4.
4. Do **not** add classes or methods not grounded in the requirements above.
