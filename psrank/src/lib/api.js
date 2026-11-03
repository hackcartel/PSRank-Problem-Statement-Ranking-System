const CATEGORY_KEYWORDS = [
  ["Health", ["clinic", "patient", "health", "care", "medical"]],
  ["Agriculture", ["food", "farm", "crop", "farmer", "grocer"]],
  ["Transportation", ["bus", "transport", "traffic", "commute", "transit"]],
  ["Climate", ["climate", "emission", "warming", "carbon", "weather"]],
  ["Education", ["school", "student", "teacher", "learning", "education"]],
  ["Energy", ["energy", "electricity", "power", "solar", "heating"]],
  ["Water", ["water", "drinking", "drain", "flood", "pipe"]],
  ["Finance", ["finance", "loan", "payment", "bank", "income"]],
  ["Governance", ["government", "council", "agency", "public service"]],
  ["Infrastructure", ["road", "bridge", "building", "infrastructure"]],
  ["Public Safety", ["safety", "emergency", "crime", "safe"]],
  ["Sanitation", ["sanitation", "waste", "toilet", "sewer", "rubbish"]],
  ["Accessibility", ["accessibility", "disability", "deaf", "accessible"]],
  ["Disaster Management", ["disaster", "flood", "fire", "storm"]],
  ["Employment", ["job", "work", "worker", "employment", "shift"]],
];

export async function mockAnalyze(problemStatement) {
  await new Promise((resolve) => window.setTimeout(resolve, 450));
  const text = problemStatement.toLowerCase();
  const words = text.trim().split(/\s+/).filter(Boolean);
  const mentions = CATEGORY_KEYWORDS.map(([category, keywords]) => ({
    category,
    count: keywords.filter((keyword) => text.includes(keyword)).length,
  })).sort((a, b) => b.count - a.count);
  const category = mentions[0].count > 0 ? mentions[0].category : "Governance";
  const detail = Math.min(10, Math.max(4, 5 + Math.floor(words.length / 20)));
  const specificity = Math.min(10, 4 + new Set(words).size % 7);
  const breakdown = {
    impact: Math.min(10, 6 + (words.length % 5)),
    feasibility: Math.min(10, 5 + (words.length % 4)),
    novelty: specificity,
    clarity: detail,
    data: Math.min(10, 4 + (text.match(/\d+/g)?.length || 0) * 2 + (text.includes("survey") ? 2 : 0)),
  };
  const totalScore = Math.round(
    (Object.values(breakdown).reduce((sum, score) => sum + score, 0) / 50) * 100,
  );
  return {
    totalScore,
    breakdown,
    category,
    reason: `This ${category.toLowerCase()} challenge describes a community need. Adding specific evidence, affected groups, and measurable outcomes could strengthen the proposal.`,
  };
}
