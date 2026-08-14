# Logic Prototype

Build one offline HTML file that a person can drive.

Keep the model in a pure JavaScript module. Use the smallest form:

- pure functions for independent transformations;
- a reducer for discrete actions;
- a state machine when legal actions depend on state;
- a state-owning module only when internal state is under test.

Show:

1. `PROTOTYPE` and the question.
2. Labelled domain state.
3. Last action and changed fields.
4. Controls for every action.
5. Deterministic happy, risky, and illegal-action scenarios.
6. Reset to a documented initial state.

Make rejected actions and invariant violations visible. Use no framework,
network, server, database, production mutation, or permanent tests.

Open the file in a browser. Run every scenario and the risky transition. Record
the observed state and verdict.
