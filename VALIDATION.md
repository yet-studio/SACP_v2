# Validation Protocol

## Core Principles
- Documentation avant action
- Tests avant code
- Qualité non négociable
- Sécurité par défaut

## Validation Process

### 1. Strategy Validation [CRITICAL]
```yaml
strategy:
  required: true
  location: docs/strategy/YYYY-MM-DD-feature-name.md
  template: |
    # Strategy Document
    ## 1. Purpose
    - What problem are we solving?
    - Why is this important?
    
    ## 2. Approach
    - How will we solve it?
    - What alternatives were considered?
    
    ## 3. Impact Analysis
    - Quality impact
    - Security implications
    - Performance considerations
    
    ## 4. Success Criteria
    - Specific metrics
    - Validation points
    - Expected outcomes

  checklist:
    - [ ] Purpose clearly defined
    - [ ] Approach detailed and justified
    - [ ] Impact analyzed
    - [ ] Success criteria specified
```

### 2. Code Validation
```yaml
code:
  required: true
  checklist:
    tests:
      - [ ] Unit tests written
      - [ ] Integration tests added
      - [ ] Security tests included
      - [ ] Performance tests done
    
    quality:
      - [ ] Code standards met
      - [ ] Documentation complete
      - [ ] Error handling robust
      - [ ] Logging appropriate
    
    security:
      - [ ] Input validated
      - [ ] Output sanitized
      - [ ] Access controlled
      - [ ] Data protected
    
    performance:
      - [ ] Complexity analyzed
      - [ ] Resources optimized
      - [ ] Bottlenecks identified
      - [ ] Benchmarks run
```

### 3. Documentation Validation
```yaml
documentation:
  required: true
  checklist:
    api:
      - [ ] Endpoints documented
      - [ ] Parameters described
      - [ ] Examples provided
      - [ ] Edge cases covered
    
    changes:
      - [ ] CHANGELOG updated
      - [ ] Breaking changes noted
      - [ ] Migration guide added
      - [ ] Version bumped
    
    impact:
      - [ ] Dependencies listed
      - [ ] Side effects noted
      - [ ] Performance impact documented
      - [ ] Security considerations detailed
```

## Validation Flow
1. Create strategy document
2. Get strategy approval
3. Write tests
4. Implement feature
5. Run validations
6. Document changes
7. Final review

## Integration Points

### With METRICS.md
- Quality metrics tracked
- Performance benchmarks recorded
- Success criteria measured
- Evolution metrics updated

### With EVOLUTION.md
- Changes documented
- Decisions recorded
- Learnings captured
- Improvements tracked

## Templates

### 1. Validation Report
```yaml
validation:
  feature: "Feature Name"
  date: YYYY-MM-DD
  status: pending|approved|rejected
  
  strategy:
    document: "docs/strategy/YYYY-MM-DD-feature-name.md"
    status: approved
  
  code:
    tests: passed
    coverage: 100%
    quality: approved
    security: verified
  
  documentation:
    status: complete
    reviewed: true
    
  notes:
    - Important observations
    - Special considerations
    - Future improvements
```

### 2. Review Checklist
```yaml
review:
  strategy:
    - Purpose clear?
    - Approach valid?
    - Impact understood?
    - Criteria defined?
  
  implementation:
    - Tests complete?
    - Code quality high?
    - Security verified?
    - Performance acceptable?
  
  documentation:
    - API documented?
    - Changes recorded?
    - Impact detailed?
    - Examples provided?
```

## Success Validation
- [ ] All validations pass
- [ ] Documentation complete
- [ ] Tests comprehensive
- [ ] Security verified
- [ ] Performance acceptable
- [ ] Changes tracked
