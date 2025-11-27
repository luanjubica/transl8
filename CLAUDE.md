# CLAUDE.md - AI Assistant Guide for transl8

## About This Document

This document serves as a comprehensive guide for AI assistants (like Claude) working on the transl8 project. It provides context about the codebase structure, development workflows, conventions, and best practices to follow when making changes.

**Last Updated:** 2025-11-27
**Project Status:** Initial Setup

---

## Project Overview

### Purpose
**transl8** - [Project description to be added as development progresses]

### Tech Stack
[To be populated as the project develops]

- **Language(s):** TBD
- **Framework(s):** TBD
- **Build Tool:** TBD
- **Package Manager:** TBD
- **Testing Framework:** TBD
- **Linting/Formatting:** TBD

---

## Repository Structure

```
transl8/
├── [Directory structure to be documented as project grows]
└── CLAUDE.md (this file)
```

### Key Directories

[To be populated as the project develops]

---

## Development Workflow

### Branch Strategy

- **Main Branch:** [To be determined]
- **Feature Branches:** Use descriptive branch names following the pattern `feature/description` or `claude/claude-md-<session-id>`
- **Development Branches:** Claude should work on branches starting with `claude/` and matching the session ID

### Commit Conventions

Follow these commit message guidelines:

1. **Format:** `<type>: <description>`
2. **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `refactor`: Code refactoring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks
   - `style`: Code style changes (formatting, etc.)

3. **Examples:**
   - `feat: add user authentication system`
   - `fix: resolve null pointer in payment processing`
   - `docs: update API documentation`

### Git Operations

**Push Commands:**
- Always use: `git push -u origin <branch-name>`
- Branch names for Claude must start with `claude/` and end with session ID
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network failures

**Fetch/Pull Commands:**
- Prefer specific branches: `git fetch origin <branch-name>`
- Retry logic same as push operations

---

## Code Conventions

### General Principles

1. **Keep It Simple:** Avoid over-engineering. Only make changes that are directly requested or clearly necessary.
2. **Security First:** Always consider security implications (XSS, SQL injection, command injection, etc.)
3. **No Premature Optimization:** Don't add abstractions or helper functions for one-time operations
4. **Clean Deletions:** Remove unused code completely—no `// removed` comments or unused parameters

### Code Style

[To be populated based on project language and conventions]

- **Indentation:** [tabs/spaces, size]
- **Naming Conventions:** [camelCase, snake_case, PascalCase, etc.]
- **File Naming:** [conventions for files]
- **Maximum Line Length:** [if applicable]

### Comments and Documentation

- Only add comments where logic isn't self-evident
- Don't add docstrings to code you didn't change
- Focus on "why" rather than "what" in comments

---

## Testing Strategy

### Running Tests

[To be populated with test commands]

```bash
# Example:
# npm test
# pytest
# cargo test
```

### Test Coverage

- Aim for [X]% code coverage
- All new features should include tests
- Bug fixes should include regression tests

### Testing Conventions

[To be populated with project-specific testing patterns]

---

## Build and Deployment

### Local Development

[To be populated with setup instructions]

```bash
# Example setup commands
```

### Build Process

[To be populated with build commands]

```bash
# Example build commands
```

### Environment Variables

[To be documented as needed]

| Variable | Purpose | Required |
|----------|---------|----------|
| TBD | TBD | Yes/No |

---

## Key Files and Their Purposes

[To be populated as project grows]

| File/Directory | Purpose | Notes |
|----------------|---------|-------|
| CLAUDE.md | AI assistant guide | This file |

---

## Common Tasks

### Adding a New Feature

1. Read existing related code first
2. Create a todo list for tracking (use TodoWrite tool)
3. Implement changes following conventions
4. Add tests for new functionality
5. Update documentation if needed
6. Commit with clear message
7. Push to feature branch

### Fixing a Bug

1. Reproduce and understand the bug
2. Read relevant code sections
3. Implement minimal fix
4. Add regression test
5. Commit and push

### Refactoring

1. Only refactor when explicitly requested
2. Ensure tests pass before and after
3. Make small, incremental changes
4. Don't combine refactoring with feature work

---

## Architecture Decisions

[To be documented as architectural patterns emerge]

### Design Patterns

[To be populated]

### API Design

[To be populated if applicable]

### Database Schema

[To be populated if applicable]

---

## Dependencies and Package Management

### Adding Dependencies

[To be documented based on package manager]

### Dependency Guidelines

- Prefer well-maintained packages
- Check licenses for compatibility
- Document why each dependency is needed
- Keep dependencies up to date

---

## Troubleshooting

### Common Issues

[To be populated as common problems are identified]

### Debug Strategies

1. Check logs first
2. Verify environment configuration
3. Ensure dependencies are installed
4. Check git branch and status

---

## Performance Considerations

[To be documented as performance requirements emerge]

---

## Security Guidelines

### Security Checklist

- [ ] Input validation at system boundaries
- [ ] No hardcoded credentials
- [ ] Proper authentication and authorization
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection (if web app)
- [ ] Secure dependencies (no known vulnerabilities)
- [ ] Environment variables for secrets

### Sensitive Files

Never commit:
- `.env` files (except `.env.example`)
- `credentials.json` or similar
- Private keys
- API tokens

---

## AI Assistant Specific Guidelines

### Before Making Changes

1. **Always read files first** - Never propose changes to code you haven't read
2. **Understand context** - Explore related files and understand how pieces fit together
3. **Check existing patterns** - Follow established conventions in the codebase

### During Implementation

1. **Use TodoWrite tool** - Track tasks for complex multi-step work
2. **Make focused changes** - One logical change per commit
3. **Test as you go** - Verify changes work before moving on
4. **Parallel tool calls** - Use multiple independent tool calls in one message when possible

### After Changes

1. **Mark todos complete** - Update todo status immediately after finishing tasks
2. **Verify tests pass** - Run test suite before committing
3. **Review your changes** - Do a final check before pushing

### Communication Style

- Be concise and technical
- Focus on facts over validation
- Use markdown for formatting
- Avoid emojis unless requested
- No time estimates in plans

---

## Resources

### Documentation

[To be populated with links to relevant docs]

### Related Projects

[To be populated if applicable]

### Contact

[To be populated with maintainer info]

---

## Change Log

### 2025-11-27
- Initial CLAUDE.md creation
- Repository initialized

---

## Notes for Future Updates

This document should be updated whenever:
- New architectural decisions are made
- Development workflows change
- New conventions are established
- Significant features are added
- Common issues are discovered

**Keep this document current to ensure AI assistants have accurate context!**
