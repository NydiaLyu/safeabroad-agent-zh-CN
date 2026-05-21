import type { TimelineEvent } from "../schemas/timeline";

export function nextNonLeadingQuestion(events: TimelineEvent[]): string {
  const hasLocation = events.some((event) => /店|街|车站|学校|门口|路/.test(event.descriptionZh));
  const hasWitness = events.some((event) => /证人|旁边|看到|围观/.test(event.descriptionZh));

  if (!hasLocation) {
    return "你记得事情开始时你大概在哪里吗？可以只说你确定的部分。";
  }

  if (!hasWitness) {
    return "你记得附近是否有人可能看到或听到吗？如果不确定，可以直接说不确定。";
  }

  return "接下来你想补充哪一个时间点？请只写你自己记得的内容。";
}
