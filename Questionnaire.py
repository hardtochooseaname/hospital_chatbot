db = {
    "糖尿病": [
        # 选择题
        "在过去一个月里，您感觉自己的血糖控制情况如何？A. 比以前好很多 B. 有所改善 C. 没有明显变化 D. 比以前差",
        "您是否按照医生的建议，定期监测自己的血糖？A. 总是 B. 大部分时间 C. 偶尔 D. 从不",
        #"您每天的饮食是否遵循了医生的饮食建议？A. 总是 B. 大部分时间 C. 偶尔 D. 从不",
        #"您是否经常感到疲劳或乏力？A. 总是 B. 大部分时间 C. 偶尔 D. 从不",

        # 判断题
        "您是否曾因糖尿病症状住院治疗过？A. 是 B. 否",
        #"您是否参加过糖尿病患者的健康教育活动或支持小组？A. 是 B. 否",
        "您觉得当前的治疗方法是否对您有效？A. 是 B. 否",

        # 简答题
        "在康复期间，您遇到了哪些困难或问题？",
        #"您觉得您的主治医生的服务态度、专业能力等怎么样？",
        "您对医院的整体服务（如就诊流程、设施等）有什么建议吗？"
    ]
}

class Questionnaire:
    def __init__(self, questions):
        self.questions = [{"question": q, "status": False, "answer": "", "type": self.determine_type(q)} for q in questions]
        self.total_questions = len(questions)
        self.pending_questions = self.total_questions

    def determine_type(self, question):
        if "A. " in question:
            return 0  # 选择题
        elif "A. 是" in question or "A. 否" in question:
            return 1  # 判断题
        else:
            return 2  # 简答题

    def get_question(self, index):
        return self.questions[index]["question"]

    def get_status(self, index):
        return self.questions[index]["status"]

    def set_status(self, index, status):
        self.questions[index]["status"] = status

    def get_answer(self, index):
        return self.questions[index]["answer"]

    def set_answer(self, index, answer):
        self.questions[index]["answer"] = answer
        if not self.questions[index]["status"]:
            self.questions[index]["status"] = True
            self.pending_questions -= 1

    def have_questions_left(self):
        return self.pending_questions > 0

    def get_pending_questions_string(self):
        return "\n".join([q["question"] for q in self.questions if not q["status"]])

    def get_question_status(self, index):
        return self.questions[index]["status"]

    def set_question_status_and_answer(self, index, status, answer):
        self.questions[index]["status"] = status
        self.questions[index]["answer"] = answer
        if status and not self.questions[index]["status"]:
            self.pending_questions -= 1

    def get_next_question(self)->list:
        for i, q in enumerate(self.questions):
            if not q["status"]:
                return [i, q["question"]]
        return []

    # 打印所有的问题与回答
    def print_all_questions_and_answers(self):
        for i, q in enumerate(self.questions):
            print(f"问题{i + 1}: {q['question']}")
            print(f"回答: {q['answer']}\n")

# 实例化一个问卷
diabetes_questionnaire = Questionnaire(db["糖尿病"])