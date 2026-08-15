Feature: /git-agent command menu
  The git-agent workflows (commit, commit-and-push, init, related) are exposed
  as a native pi /git-agent menu, not as skills. Each menu item embeds its
  procedure inline via pi.sendUserMessage.

  Background:
    Given the pi-git-agent package is installed
    And package.json registers extensions only (no skills)

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
    Then the agent follows procedures/commit.md (session_context first, then git-agent commit)

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

  Scenario: Guidance emphasizes proactive co-change intelligence over redundant commit instructions
    Given the before_agent_start extension hook
    When guidance is injected into the system prompt
    Then it highlights git-agent related for multi-file blast radius and test discovery
    And it leaves commit mechanics to the tool guard and procedure

  Scenario: Full delegation to git-agent commit
    Given the agent is ready to commit changes
    When the agent follows procedures/commit.md
    Then the agent builds intent from session_context
    And the agent delegates staging, atomic splitting, auto-scoping, and hook validation directly to git-agent commit

  Scenario: Configuration precedence distinguishes model inference from session attribution
    Given the references/cli.md documentation
    Then config precedence specifies CLI flags over local git config and global config
    And agent session environment variables are documented as attribution-only

  Scenario: No skill surface remains
    Given the package tree
    Then there is no skills/ directory
    And no procedure references /skill:...
