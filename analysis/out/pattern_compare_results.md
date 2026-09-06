# Pattern comparison — DI styles and maintainability proxies

- **Sample:** 402 accepted repos; style, AST, and GitHub signals joined. 
GitHub issue signals available for 384 repos (95.5%).

- **Design & honesty:** cross-sectional, observational, proxy outcomes. 
Standardized OLS (outcome and predictors z-scored) with HC1 robust SEs, 
controlling for stars, age, size, Python share, and tutorial flag. 
Effect sizes and CIs are *associations*, not causal claims; the low-n 
Tier B idiom groups (n=1-15) mean a *ranking* of patterns is not statistically resolvable here. We report direction/magnitude evidence only.

## Outcome means by DI style

| style | n | hygiene | sophist. | func_len | branch/fn | doc% | type-ann% | issues/1kLOC | contribs |
|---|---|---|---|---|---|---|---|---|---|
| bare-function dominant | 279 | 3.27 | 6.5 | 20.6 | 2.56 | 43 | 92 | 0.36 | 5 |
| zero-DI | 98 | 2.72 | 4.9 | 21.8 | 3.07 | 47 | 88 | 0.18 | 26 |
| class-as-dependency | 7 | 3.71 | 7.3 | 17.9 | 1.98 | 64 | 84 | 1.24 | 6 |
| current_* request-scope | 15 | 3.33 | 7.7 | 21.4 | 2.68 | 51 | 95 | 0.15 | 4 |
| module-alias deps | 3 | 2.67 | 4.3 | 21.2 | 2.94 | 34 | 86 | 0.06 | 28 |


## Outcome: hygiene (engineering-hygiene composite (0..5))

n=402, R^2=0.14 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.033 **[-0.037, 0.104]** | 
| class-as-dependency Depends(Class) | -0.063 **[-0.178, 0.051]** | 
| current_* request-scope injection | -0.019 **[-0.117, 0.079]** | 
| module-alias deps (mod.dep) | 0.266 **[0.169, 0.364]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.085 **[-0.006, 0.176]** | 
| Annotated[...] typed injection | -0.150 **[-0.506, 0.206]** | 


## Outcome: sophistication_index (structural sophistication index)

n=402, R^2=0.27 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.028 **[-0.047, 0.103]** | 
| class-as-dependency Depends(Class) | -0.072 **[-0.183, 0.040]** | 
| current_* request-scope injection | 0.000 **[-0.086, 0.087]** | 
| module-alias deps (mod.dep) | 0.350 **[0.264, 0.436]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.092 **[0.007, 0.177]** | *sig.*
| Annotated[...] typed injection | -0.211 **[-0.521, 0.099]** | 


## Outcome: mean_func_len (mean function length (LOC))

n=402, R^2=0.22 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.037 **[-0.048, 0.122]** | 
| class-as-dependency Depends(Class) | -0.001 **[-0.073, 0.070]** | 
| current_* request-scope injection | -0.047 **[-0.136, 0.041]** | 
| module-alias deps (mod.dep) | 0.426 **[0.334, 0.518]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.103 **[0.014, 0.193]** | *sig.*
| Annotated[...] typed injection | -0.059 **[-0.364, 0.247]** | 


## Outcome: mean_branch_per_func (mean branch density per function)

n=402, R^2=0.32 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.076 **[-0.065, 0.216]** | 
| class-as-dependency Depends(Class) | 0.012 **[-0.067, 0.090]** | 
| current_* request-scope injection | -0.160 **[-0.244, -0.076]** | *sig.*
| module-alias deps (mod.dep) | 0.434 **[0.349, 0.520]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.044 **[-0.036, 0.125]** | 
| Annotated[...] typed injection | 0.164 **[-0.125, 0.453]** | 


## Outcome: docstring_share (docstring coverage %)

n=402, R^2=0.10 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.028 **[-0.056, 0.111]** | 
| class-as-dependency Depends(Class) | -0.027 **[-0.106, 0.051]** | 
| current_* request-scope injection | 0.013 **[-0.085, 0.111]** | 
| module-alias deps (mod.dep) | 0.285 **[0.189, 0.380]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.012 **[-0.085, 0.109]** | 
| Annotated[...] typed injection | -0.035 **[-0.395, 0.326]** | 


## Outcome: type_ann_share (type-annotation share %)

n=402, R^2=0.16 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | -0.043 **[-0.127, 0.041]** | 
| class-as-dependency Depends(Class) | -0.243 **[-0.488, 0.001]** | 
| current_* request-scope injection | 0.032 **[-0.058, 0.122]** | 
| module-alias deps (mod.dep) | 0.121 **[0.022, 0.219]** | *sig.*
| hub-rich graph (>=3-consumer hub) | -0.011 **[-0.100, 0.077]** | 
| Annotated[...] typed injection | -0.227 **[-0.547, 0.093]** | 


## Outcome: open_issues_ratio (open issues per 1k LOC)

n=384, R^2=0.11 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.130 **[-0.042, 0.302]** | 
| class-as-dependency Depends(Class) | 0.007 **[-0.125, 0.140]** | 
| current_* request-scope injection | -0.122 **[-0.246, 0.003]** | 
| module-alias deps (mod.dep) | -0.211 **[-0.370, -0.052]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.058 **[-0.035, 0.150]** | 
| Annotated[...] typed injection | -0.479 **[-1.237, 0.278]** | 


## Outcome: log_contributors (log1p(# contributors))

n=402, R^2=0.21 — standardized beta [95% CI] (continuous predictors z-scored; binary predictors 0/1)

| predictor | beta | 95% CI |
|---|---|---|
| zero-DI (no DI constructs) | 0.315 **[0.156, 0.473]** | *sig.*
| class-as-dependency Depends(Class) | 0.044 **[-0.043, 0.130]** | 
| current_* request-scope injection | -0.013 **[-0.087, 0.061]** | 
| module-alias deps (mod.dep) | 0.229 **[0.089, 0.370]** | *sig.*
| hub-rich graph (>=3-consumer hub) | 0.092 **[-0.006, 0.191]** | 
| Annotated[...] typed injection | -0.107 **[-0.418, 0.203]** | 


## Reading (honest)

- Any beta whose CI excludes 0 is marked; otherwise direction is consistent with noise.
- Positive beta = style associated with *higher* outcome. For func_len/branch density higher = more complex (worse); for doc%/ann% higher = better; hygiene/contribs higher = healthier.
- Zero-DI and Tier B groups are small: treat their estimates as evidence-of-direction, not rankings.

