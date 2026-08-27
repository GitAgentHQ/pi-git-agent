Feature: /git-agent command menu
  The git-agent workflows (commit, commit-and-push, init, related) are exposed
  as a native pi /git-agent menu, not as skills. Each menu item embeds its
  procedure inline via pi.sendUserMessage.

  Background:
    Given the pi-git-agent package is installed
    And package.json registers extensions only (no skills)

  Scenario: Package uses a root index entrypoint
    Given the pi-git-agent package is installed
    Then package.json points Pi at ./index.ts
    And index.ts delegates to src/index.ts
    And src/index.ts registers the menu, session context, and commit guard extensions

  Scenario: Menu lists all workflows
    When the user types /git-agent
    Then a select dialog shows Commit changes, Commit and push, Init / optimize, and Related files & tests

  Scenario: Selecting an item delivers the procedure inline
    Given the user picks "Commit changes"
    When the menu handler sends the follow-up message
    Then the message embeds procedures/commit.md verbatim
    And the message resolves {{PKG_DIR}} to the installed package dir

  Scenario: Keyword shorthand skips the menu
    When the user types "/git-agent commit --co-author \"Alice\""
    Then the commit workflow runs directly with invocation args "--co-author \"Alice\""

  Scenario: Natural language still routes without a skill
    When the user asks to "commit this"
    Then the agent follows procedures/commit.md (session_context first, then bare git-agent --intent)

  Scenario: session_context excludes the menu's own injected procedure
    Given the user opened the /git-agent menu and picked "Commit changes"
    When the session_context tool builds the commit intent
    Then the message starting with Run the "Commit changes" workflow. is not listed as a user request

  Scenario: session_context collapses expanded skill invocations
    Given a user message contains an expanded skill block "<skill name=\"web-perf\" location=\"...\">...long prompt...</skill>" with arguments "audit the site"
    When the session_context tool extracts the user request
    Then the skill prompt body is collapsed to "[Invoked skill: web-perf]"
    And the user arguments "audit the site" are preserved

  Scenario: session_context handles skill invocations with no arguments
    Given a user message contains an expanded skill block "<skill name=\"commit\" location=\"...\">...long prompt...</skill>" without arguments
    When the session_context tool extracts the user request
    Then the skill prompt body is collapsed to "[Invoked skill: commit]"
    And the internal skill prompt instructions are omitted

  Scenario: No before_agent_start guidance is injected
    Given the before_agent_start extension hook
    When the extension starts
    Then no Git Intelligence & Co-Change Analysis guidance is injected into the system prompt
    And commit mechanics remain in the post-tool guard and procedure

  Scenario: Guard blocks raw git commit and prepares intent context locally
    Given the agent tries to run raw "git commit"
    When the tool_call extension inspects the bash command
    Then the call is blocked with a reason requiring "git-agent --intent \"<intent>\"" built from session context
    And the reason includes locally extracted session context
    And the reason directly tells the agent to run git-agent without calling session_context
    And the reason does not mention the /git-agent menu

  Scenario: Guard allows raw git add
    Given the agent tries to run raw "git add src/"
    When the tool_call extension inspects the bash command
    Then the call is not blocked

  Scenario: Guard context shares session_context extraction and has a bounded length
    Given the guard handles a raw "git commit" tool call
    When it extracts session context locally
    Then it uses the same extraction function as the session_context tool
    And it does not ask the agent to call session_context again
    And the context included in the block reason is length-bounded

  Scenario: Commit intent reset recognizes both bare and subcommand invocations
    Given a session bash entry ran "git-agent --intent \"ship it\""
    When session_context decides which entries are already-consumed context
    Then the bare invocation counts as a commit boundary
    And so does "git-agent commit --intent \"ship it\""

  Scenario: session_context renders a compact monitor-style lifecycle row
    Given the session_context tool is called
    When it extracts requests from the session
    Then it returns the shared bounded context text
    And its call slot is empty
    And its result row uses pi-kit's lifecycle label and expansion helper
    And the collapsed row appends the configured expansion key
    And expanded rendering reveals bounded context details
    And an empty session uses the subject `no user requests`

  Scenario: session_context stays quiet when the session has no user messages
    Given a session with no extractable user messages
    When session_context completes
    Then the collapsed row reads "[context] gathered · no user requests" instead of a full report

  Scenario: Full delegation to bare git-agent --intent
    Given the agent is ready to commit changes
    When the agent follows procedures/commit.md
    Then the agent builds intent from session_context
    And the agent delegates staging, atomic splitting, auto-scoping, and hook validation directly to bare "git-agent --intent"

  Scenario: Configuration precedence distinguishes model inference from session attribution
    Given the references/cli.md documentation
    Then config precedence specifies CLI flags over local git config and global config
    And agent session environment variables are documented as attribution-only

  Scenario: No skill surface remains
    Given the package tree
    Then there is no skills/ directory
    And no procedure references /skill:...
