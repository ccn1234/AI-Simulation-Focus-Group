export type ProductAnalysis = {
  core_value_proposition: string;
  expected_purchase_motivations: string[];
  expected_resistance_factors: string[];
  main_competitors_or_alternatives: string[];
  copy_strengths: string[];
  copy_weaknesses: string[];
  target_fit_summary: string;
};

export type Persona = {
  id: number;
  name: string;
  age: number;
  gender: string;
  job: string;
  income_level: string;
  personality: string;
  pain_point: string;
  purchase_barrier: string;
  region: string;
  marital_status: string;
  has_children: boolean;
  lifestyle: string;
  ai_familiarity: string;
  brand_sensitivity: string;
  price_sensitivity: string;
  current_solutions: string[];
  decision_style: string;
  frequently_used_apps: string[];
  information_channels: string[];
  past_failure_experience: string;
  reaction_type: string;
};

export type PersonaResponse = {
  persona_id: number;
  first_impression: string;
  positive_points: string[];
  concerns: string[];
  purchase_intent_score: number;
  memorable_quote: string;
  suggested_improvement: string;
};

export type SummaryReport = {
  overall_score: number;
  key_insights: string[];
  key_positive_reactions: string[];
  key_negative_reactions: string[];
  strongest_target_segment: string;
  weakest_point: string;
  improvement_priorities: string[];
  recommended_next_actions: string[];
};

export type DiscussionMessage = {
  speaker_name: string;
  speaker_role: string;
  message: string;
  stance: 'agree' | 'disagree' | 'neutral' | 'changed_mind' | 'challenge' | 'support';
  related_issue: 'price' | 'trust' | 'privacy' | 'convenience' | 'effectiveness' | 'habit' | 'brand';
};

export type PurchaseIntentChange = {
  persona_name: string;
  before_score: number;
  after_score: number;
  change_reason: string;
};

export type DiscussionSummary = {
  main_conflicts: string[];
  agreements: string[];
  changed_opinions: string[];
  final_group_consensus: string;
  purchase_intent_changes: PurchaseIntentChange[];
};

export type DiscussionResult = {
  discussion_messages: DiscussionMessage[];
  discussion_summary: DiscussionSummary;
};

export type SimulationResult = {
  product_analysis: ProductAnalysis;
  personas: Persona[];
  responses: PersonaResponse[];
  summary_report: SummaryReport;
  discussion_result: DiscussionResult;
};

export type SimulationRequestPayload = {
  product_name: string;
  product_description: string;
  target_audience: string;
  ad_copy: string;
};
