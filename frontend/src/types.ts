export interface RoleSummary {
  id: string;
  name: string;
  summary: string;
  builds_on: string | null;
  competency_count: number;
  foundational_tools: string[];
}

export interface RolesResponse {
  roles: RoleSummary[];
  knowledge_backend: string;
}

/** A human source line for the grounded-knowledge layer. Never fabricated. */
export function groundingLabel(backend: string | null | undefined): string {
  if (backend === "foundry_iq") return "Grounded by Foundry IQ";
  if (backend === "local") return "Grounded by the local corpus";
  return "";
}

export type StepMode = "deterministic" | "model" | "code" | "none";

export interface Step {
  agent: string;
  action: string;
  mode: StepMode;
  detail: string;
  elapsed_ms: number;
}

export interface Question {
  competency_id: string;
  competency_name: string;
  question: string;
}

export interface AssessmentStart {
  role: { id: string; name: string; summary: string; builds_on: string | null; foundational_tools: string[] };
  questions: Question[];
  knowledge_backend: string;
  steps: Step[];
}

export interface CompetencyResult {
  competency_id: string;
  name: string;
  weight: number;
  target_level: string;
  attained_level: string;
  target_value: number;
  attained_value: number;
  coverage: number;
  meets_target: boolean;
  gap_levels: number;
  assessed: boolean;
}

export interface Evaluation {
  competency_id: string;
  competency_name: string;
  question: string;
  level: string;
  score: number;
  rationale: string;
}

export interface Citation {
  doc_id: string;
  title: string;
  text: string;
  score: number;
  source: string;
  citation: string;
}

export interface LearningPlan {
  competency_id: string;
  name: string;
  attained_level: string;
  target_level: string;
  summary: string;
  modules: { title: string; focus: string }[];
  citations: Citation[];
}

export interface NextStep {
  competency_id: string;
  name: string;
  from_level: string;
  to_level: string;
  weight: number;
  action: string;
}

export interface ResultData {
  role_id: string;
  role_name: string;
  readiness_percent: number;
  threshold: string;
  competencies: CompetencyResult[];
  strengths: CompetencyResult[];
  gaps: CompetencyResult[];
  evaluations: Evaluation[];
  narrative: string;
  next_steps: NextStep[];
  learning_plans: LearningPlan[];
  knowledge_backend: string;
  model_configured: boolean;
  steps: Step[];
}
