export type RiskLevel = "RED" | "YELLOW" | "GREEN";

export function classifySafetyRisk(text: string): RiskLevel {
  if (/还在|门口|跟踪|追我|马上|现在|流血|不能呼吸|自杀|伤害自己/.test(text)) {
    return "RED";
  }

  if (/害怕|睡不着|受伤|疼|威胁|恐吓|不敢/.test(text)) {
    return "YELLOW";
  }

  return "GREEN";
}
