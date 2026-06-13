import type { AssessmentStart, ResultData, RolesResponse } from "./types";

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error((detail as { error?: string }).error ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function fetchRoles(): Promise<RolesResponse> {
  const res = await fetch("/api/roles");
  if (!res.ok) throw new Error("Could not load roles");
  return (await res.json()) as RolesResponse;
}

export function startAssessment(roleId: string): Promise<AssessmentStart> {
  return postJson<AssessmentStart>("/api/assessment", { role_id: roleId });
}

export function submitAnswers(
  roleId: string,
  answers: { competency_id: string; question: string; answer: string }[],
): Promise<ResultData> {
  return postJson<ResultData>("/api/result", { role_id: roleId, answers });
}
