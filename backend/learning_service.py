"""
学习中心核心服务
实现四阶段交叉学习模式
"""
import random
import json
from datetime import datetime, timedelta, date
from backend.models import db, User, Word, LearningRecord, ReviewSchedule, LearningProgress, UserLearningSettings, DailyPlan, LearningChoiceOptions

# 阶段名称映射
STAGE_NAMES = {
    1: '看视频学习',
    2: '选择题',
    3: '看视频输入',
    4: '手势识别'
}

# 阶段描述映射
STAGE_DESCRIPTIONS = {
    1: '观看词汇演示视频，学习动作分解',
    2: '从四个选项中选择正确的词汇',
    3: '观看视频后在输入框输入词汇',
    4: '打出手势让系统识别是否正确'
}


class LearningCenterService:
    """学习中心核心服务"""

    @staticmethod
    def get_or_create_settings(user_id):
        """获取或创建设置"""
        settings = UserLearningSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserLearningSettings(
                user_id=user_id,
                daily_new_words=3,
                daily_review_words=5
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    @staticmethod
    def update_settings(user_id, daily_new_words=None, daily_review_words=None):
        """更新学习设置"""
        settings = LearningCenterService.get_or_create_settings(user_id)
        if daily_new_words is not None:
            settings.daily_new_words = max(1, min(20, daily_new_words))
        if daily_review_words is not None:
            settings.daily_review_words = max(1, min(50, daily_review_words))
        db.session.commit()
        return settings.to_dict()

    @staticmethod
    def get_today_plan(user_id):
        """获取今日学习计划"""
        today = date.today()

        # 获取或创建今日计划
        plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()
        if not plan:
            plan = LearningCenterService._generate_daily_plan(user_id, today)

        # 获取设置
        settings = LearningCenterService.get_or_create_settings(user_id)

        # 计算进度
        new_word_ids = json.loads(plan.new_word_ids) if plan.new_word_ids else []
        review_word_ids = json.loads(plan.review_word_ids) if plan.review_word_ids else []

        # 获取复习词的详细信息（包含遗忘风险）
        review_words_data = []
        if review_word_ids:
            review_schedules = ReviewSchedule.query.filter(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.word_id.in_(review_word_ids)
            ).all()
            schedule_map = {s.word_id: s for s in review_schedules}
            words = Word.query.filter(Word.id.in_(review_word_ids)).all()
            word_map = {w.id: w for w in words}

            for word_id in review_word_ids:
                schedule = schedule_map.get(word_id)
                word = word_map.get(word_id)
                if word and schedule:
                    # 计算遗忘风险
                    forget_risk = LearningCenterService._calculate_forget_risk(schedule)
                    review_words_data.append({
                        'word_id': word_id,
                        'word': word.word,
                        'forget_risk': forget_risk,
                        'interval': schedule.interval,
                        'correct_count': schedule.correct_count
                    })

        # 获取新词的详细信息
        new_words_data = []
        if new_word_ids:
            words = Word.query.filter(Word.id.in_(new_word_ids)).all()
            for w in words:
                new_words_data.append({
                    'word_id': w.id,
                    'word': w.word,
                    'category': w.category,
                    'difficulty': w.difficulty
                })

        return {
            'plan': plan.to_dict(),
            'settings': settings.to_dict(),
            'new_words_total': len(new_word_ids),
            'review_words_total': len(review_word_ids),
            'learned_count': plan.learned_count,
            'reviewed_count': plan.reviewed_count,
            'new_words_completed': plan.learned_count >= len(new_word_ids) if new_word_ids else True,
            'review_completed': plan.reviewed_count >= len(review_word_ids) if review_word_ids else True,
            'is_all_completed': plan.is_completed,
            'new_words': new_words_data,
            'review_words': review_words_data
        }

    @staticmethod
    def _calculate_forget_risk(schedule):
        """
        计算遗忘风险
        遗忘风险 = 1 - (距今天数 / 预期间隔)
        风险值范围 0-1，越大越需要复习
        """
        if not schedule.next_review_at:
            return 1.0

        days_since_due = (datetime.now() - schedule.next_review_at).days
        if days_since_due <= 0:
            # 还没到复习时间，风险较低
            return max(0, 1 - (1 - days_since_due / schedule.interval))
        else:
            # 已经过期，风险很高
            return min(1.0, days_since_due / schedule.interval + 0.5)

    @staticmethod
    def _generate_daily_plan(user_id, plan_date):
        """生成每日计划"""
        settings = LearningCenterService.get_or_create_settings(user_id)
        daily_new = settings.daily_new_words
        daily_review = settings.daily_review_words

        # 获取已学会的词汇
        learned_word_ids = [r.word_id for r in LearningRecord.query.filter_by(
            user_id=user_id, is_learned=True
        ).all()]

        # 获取今日复习词汇（按遗忘风险排序）
        # 遗忘风险高的先出现
        review_schedules = ReviewSchedule.query.filter(
            ReviewSchedule.user_id == user_id,
            ReviewSchedule.next_review_at <= datetime.now()
        ).all()

        # 按遗忘风险排序
        review_with_risk = []
        for rs in review_schedules:
            risk = LearningCenterService._calculate_forget_risk(rs)
            review_with_risk.append((rs, risk))

        # 风险高的排前面，同时错题优先
        review_with_risk.sort(key=lambda x: (-x[1], -x[0].correct_count))
        review_word_ids = [rs.word_id for rs, risk in review_with_risk[:daily_review]]

        # 获取新词（未学过的词，按词书顺序打散）
        # 假设词书顺序由 Word 表的 id 或 list_order 字段决定
        all_words = Word.query.filter(Word.id.notin_(learned_word_ids)).order_by(Word.id).all()
        unlearned_word_ids = [w.id for w in all_words]

        # 分组打散：每3个词为一组随机打乱
        new_word_ids = LearningCenterService._shuffle_by_group(unlearned_word_ids, daily_new)

        # 创建计划
        plan = DailyPlan(
            user_id=user_id,
            plan_date=plan_date,
            new_word_ids=json.dumps(new_word_ids),
            review_word_ids=json.dumps(review_word_ids),
            learned_count=0,
            reviewed_count=0,
            is_completed=False
        )
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def _shuffle_by_group(word_ids, limit):
        """
        分组打散函数
        按词书顺序，但每3-5个词为一组随机打乱
        """
        if not word_ids:
            return []

        # 每组3个词
        group_size = 3
        groups = []
        for i in range(0, len(word_ids), group_size):
            group = word_ids[i:i + group_size]
            random.shuffle(group)
            groups.append(group)

        # 打乱各组顺序
        random.shuffle(groups)

        # 展开并取前 limit 个
        result = []
        for group in groups:
            result.extend(group)
            if len(result) >= limit:
                break

        return result[:limit]

    @staticmethod
    def start_session(user_id, session_type):
        """
        开始学习/复习会话
        返回：阶段队列的第一题
        """
        if session_type not in ['learn', 'review']:
            return None, '无效的会话类型'

        today = date.today()
        plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()
        if not plan:
            plan = LearningCenterService._generate_daily_plan(user_id, today)

        if session_type == 'learn':
            word_ids = json.loads(plan.new_word_ids) if plan.new_word_ids else []
            max_stage = 4
        else:
            word_ids = json.loads(plan.review_word_ids) if plan.review_word_ids else []
            max_stage = 3  # 复习无阶段1

        if not word_ids:
            return None, f'今日{("学习" if session_type == "learn" else "复习")}计划为空'

        # 生成阶段队列
        queue = LearningCenterService._generate_session_queue(user_id, word_ids, session_type, max_stage)

        return {
            'session_type': session_type,
            'total_questions': len(queue),
            'word_count': len(word_ids),
            'queue': queue,
            'current_index': 0
        }, None

    @staticmethod
    def _generate_session_queue(user_id, word_ids, session_type, max_stage):
        """
        生成阶段队列 - 阶段优先顺序
        规则：同阶段的所有词先处理，答错的重新排队
        例如：a,b,c,d 四个词，4个阶段
        正常生成：a1→b1→c1→d1→a2→b2→c2→d2→a3→b3→c3→d3→a4→b4→c4→d4
        如果 b1 答错：a1→b1→c1→d1→a2→b1(重试)→c2→d2→a3→c3→d3→a4→c4→d4...
        """
        queue = []
        words = Word.query.filter(Word.id.in_(word_ids)).all()
        word_map = {w.id: w for w in words}

        # 获取已通过的阶段记录
        progress_records = LearningProgress.query.filter(
            LearningProgress.user_id == user_id,
            LearningProgress.word_id.in_(word_ids),
            LearningProgress.session_type == session_type
        ).all()
        progress_map = {p.word_id: p for p in progress_records}

        # 阶段优先：所有词同阶段处理
        for stage in range(1, max_stage + 1):
            for word_id in word_ids:
                word = word_map.get(word_id)
                if not word:
                    continue

                progress = progress_map.get(word_id)

                # 检查该阶段是否已完成或跳过
                stage_passed = False
                stage_skipped = False
                if progress:
                    if stage == 1:
                        stage_passed = progress.stage1_passed
                        stage_skipped = progress.stage1_skipped
                    elif stage == 2:
                        stage_passed = progress.stage2_passed
                    elif stage == 3:
                        stage_passed = progress.stage3_passed
                    elif stage == 4:
                        stage_passed = progress.stage4_passed

                # 复习模式阶段1跳过
                if session_type == 'review' and stage == 1:
                    stage_skipped = True
                    stage_passed = True

                # 如果已完成或跳过，跳过该项
                if stage_passed or stage_skipped:
                    continue

                item = {
                    'word_id': word_id,
                    'word': word.word,
                    'stage': stage,
                    'stage_name': STAGE_NAMES[stage],
                    'stage_description': STAGE_DESCRIPTIONS[stage],
                    'session_type': session_type
                }

                # 阶段1需要词汇详情（视频、图片、步骤）
                if stage == 1:
                    item['video_url'] = word.demo_video_url
                    item['image_url'] = word.image_url
                    item['steps'] = json.loads(word.steps) if word.steps else []
                    item['tips'] = json.loads(word.tips) if word.tips else []
                    item['category'] = word.category
                    item['difficulty'] = word.difficulty

                # 阶段2需要选择题选项
                if stage == 2:
                    choice_data = LearningCenterService._get_or_create_choice_options(
                        user_id, word_id, session_type, word
                    )
                    item['question_text'] = choice_data['question_text']
                    item['options'] = choice_data['options']
                    item['correct_index'] = choice_data['correct_index']
                    item['correct_word_id'] = word_id

                # 阶段3需要视频
                if stage == 3:
                    item['video_url'] = word.demo_video_url
                    item['image_url'] = word.image_url

                # 阶段4需要词汇用于识别
                if stage == 4:
                    item['target_word'] = word.word
                    item['category'] = word.category

                queue.append(item)

        return queue

    @staticmethod
    def _has_sign_language_description(word):
        """检查词汇是否有手语描述"""
        steps = json.loads(word.steps) if word.steps else []
        tips = json.loads(word.tips) if word.tips else []
        return bool(steps or tips)

    @staticmethod
    def _get_or_create_choice_options(user_id, word_id, session_type, target_word):
        """获取或创建选择题选项（基于动作描述的选择题）"""
        # 先检查缓存
        cached = LearningChoiceOptions.query.filter_by(
            user_id=user_id,
            word_id=word_id,
            session_type=session_type
        ).first()

        # 获取目标词汇的动作描述（steps 或 tips）
        steps = json.loads(target_word.steps) if target_word.steps else []
        tips = json.loads(target_word.tips) if target_word.tips else []

        # 生成题目描述
        if steps:
            # 使用动作分解步骤作为描述
            question_text = '\n'.join(f'{i+1}. {s}' for i, s in enumerate(steps))
        elif tips:
            question_text = '；'.join(tips)
        else:
            question_text = '请看下面的手语动作描述'

        if cached:
            return {
                'question_text': question_text,
                'options': json.loads(cached.options),
                'correct_index': cached.correct_index
            }

        # 只选择有手语描述的词作为候选
        all_words = Word.query.filter(Word.id != word_id).all()
        words_with_description = [w for w in all_words if LearningCenterService._has_sign_language_description(w)]

        # 如果没有足够的带描述的词，则使用全部词（理论上不应该发生）
        if not words_with_description:
            words_with_description = all_words

        # 优先选择同分类的词作为干扰项
        same_category = [w for w in words_with_description if w.category == target_word.category]
        if len(same_category) >= 3:
            distractors = random.sample(same_category, 3)
        else:
            # 如果同分类不够，从其他有手语描述的词中随机选择
            others = [w for w in words_with_description if w.category != target_word.category and w not in same_category]
            needed = 3 - len(same_category)
            if len(others) >= needed:
                distractors = same_category + random.sample(others, needed)
            else:
                # 其他词也不够，继续从所有候选词中补充
                remaining = [w for w in words_with_description if w not in same_category and w not in distractors]
                distractors = same_category + others + random.sample(remaining, min(needed, len(remaining)))

        # 构建选项（包含 id 和 word）
        options = [{'id': target_word.id, 'word': target_word.word}]
        for d in distractors:
            options.append({'id': d.id, 'word': d.word})

        random.shuffle(options)
        correct_index = next(i for i, opt in enumerate(options) if opt['id'] == target_word.id)

        # 保存到缓存
        cached = LearningChoiceOptions(
            user_id=user_id,
            word_id=word_id,
            session_type=session_type,
            options=json.dumps(options),
            correct_index=correct_index
        )
        db.session.add(cached)
        db.session.commit()

        return {
            'question_text': question_text,
            'options': options,
            'correct_index': correct_index
        }

    @staticmethod
    def submit_answer(user_id, word_id, session_type, stage, answer_data, remaining_word_ids=None):
        """
        提交答案并更新进度
        answer_data: {
            'stage1_learned': bool,  # 阶段1：确认已学习
            'stage2_choice': int,     # 阶段2：选择的选项索引 (-1=不确定)
            'stage3_input': str,      # 阶段3：输入的词汇
            'stage4_correct': bool     # 阶段4：手势识别是否正确
        }
        remaining_word_ids: 剩余未完成的词汇ID列表（按阶段优先顺序）
        """
        # 获取或创建进度记录
        progress = LearningProgress.query.filter_by(
            user_id=user_id,
            word_id=word_id,
            session_type=session_type
        ).first()

        if not progress:
            progress = LearningProgress(
                user_id=user_id,
                word_id=word_id,
                session_type=session_type,
                current_stage=1
            )
            db.session.add(progress)

        is_correct = False
        is_uncertain = False
        is_completed = False

        if stage == 1:
            # 看视频学习 - 确认已学习即可
            progress.stage1_passed = True
            progress.current_stage = 2
            is_correct = True

        elif stage == 2:
            # 选择题
            selected_index = answer_data.get('stage2_choice', -1)
            if selected_index == -1:
                is_uncertain = True
            else:
                # 获取正确答案
                cached = LearningChoiceOptions.query.filter_by(
                    user_id=user_id,
                    word_id=word_id,
                    session_type=session_type
                ).first()
                if cached:
                    correct_index = cached.correct_index
                    is_correct = (selected_index == correct_index)
                    progress.stage2_passed = is_correct
                    if is_correct:
                        progress.current_stage = 3

        elif stage == 3:
            # 看视频输入
            user_input = answer_data.get('stage3_input', '').strip()
            if not user_input:
                is_uncertain = True
            else:
                word = Word.query.get(word_id)
                is_correct = (user_input == word.word)
                progress.stage3_passed = is_correct
                if is_correct:
                    progress.current_stage = 4

        elif stage == 4:
            # 手势识别
            is_correct = answer_data.get('stage4_correct', False)
            progress.stage4_passed = is_correct
            if is_correct:
                progress.current_stage = 5
                progress.is_completed = True
                is_completed = True

                # 更新每日计划的完成计数
                today = date.today()
                plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()
                if plan:
                    if session_type == 'learn':
                        plan.learned_count += 1
                        if plan.learned_count >= len(json.loads(plan.new_word_ids or '[]')):
                            plan.is_completed = plan.reviewed_count >= len(json.loads(plan.review_word_ids or '[]'))
                    else:
                        plan.reviewed_count += 1
                        if plan.reviewed_count >= len(json.loads(plan.review_word_ids or '[]')):
                            plan.is_completed = plan.learned_count >= len(json.loads(plan.new_word_ids or '[]'))

                # 更新学习记录
                LearningCenterService._update_learning_record(user_id, word_id, is_correct)

                # 完成词汇学习/复习，奖励积分
                # 新词学习完成奖励2积分，复习完成奖励1积分
                try:
                    from backend.services import PointsService
                    if session_type == 'learn':
                        PointsService.add_points(user_id, 2, 'learning')
                    else:
                        PointsService.add_points(user_id, 1, 'review')
                except Exception:
                    pass

        db.session.commit()

        # 计算下一题
        max_stage = 4 if session_type == 'learn' else 3
        next_question = None

        if remaining_word_ids is None:
            # 如果没有提供剩余词汇列表，从每日计划获取
            today = date.today()
            plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()
            if plan:
                all_word_ids = json.loads(plan.new_word_ids or '[]') + json.loads(plan.review_word_ids or '[]')
            else:
                all_word_ids = []
        else:
            all_word_ids = remaining_word_ids

        if all_word_ids:
            # 答错时跳过当前词当前阶段
            skip_word_id = word_id if (not is_correct or is_uncertain) else None
            skip_stage = stage if (not is_correct or is_uncertain) else None

            # 答对的词记录下来，用于判断是否进入下一阶段
            answered_ids = None if (not is_correct or is_uncertain) else {word_id}

            next_question = LearningCenterService._get_next_valid_question(
                user_id, all_word_ids, session_type, max_stage, skip_word_id, skip_stage, answered_ids
            )

        # 构建返回结果
        result = {
            'is_correct': is_correct,
            'is_uncertain': is_uncertain,
            'is_completed': is_completed,
            'current_stage': progress.current_stage,
            'word_id': word_id,
            'session_type': session_type,
            'next_question': next_question,
            'is_session_complete': next_question is None and (not is_correct or is_uncertain)
        }

        return result

    @staticmethod
    def _update_learning_record(user_id, word_id, is_correct):
        """更新学习记录"""
        record = LearningRecord.query.filter_by(user_id=user_id, word_id=word_id).first()

        if not record:
            record = LearningRecord(
                user_id=user_id,
                word_id=word_id,
                practice_count=0,
                correct_count=0
            )
            db.session.add(record)

        record.practice_count += 1
        if is_correct:
            record.correct_count += 1
        record.avg_accuracy = record.correct_count / record.practice_count
        record.last_practice_at = datetime.now()

        # 判断是否满足"已学会"条件
        if not record.is_learned:
            total = record.practice_count
            correct = record.correct_count
            # 3次练习中至少2次成功，或连续2次成功
            if (total >= 3 and correct >= 2) or (correct >= 2 and correct == total):
                record.is_learned = True
                # 创建复习计划
                schedule = ReviewSchedule.query.filter_by(user_id=user_id, word_id=word_id).first()
                if not schedule:
                    schedule = ReviewSchedule(
                        user_id=user_id,
                        word_id=word_id,
                        interval=1,
                        next_review_at=datetime.now() + timedelta(days=1)
                    )
                    db.session.add(schedule)

        db.session.commit()

    @staticmethod
    def get_progress_summary(user_id):
        """获取学习进度摘要"""
        # 获取今日计划
        today = date.today()
        plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()

        if not plan:
            return {
                'today_learned': 0,
                'today_total': 0,
                'today_reviewed': 0,
                'review_total': 0,
                'is_all_completed': True
            }

        new_word_ids = json.loads(plan.new_word_ids) if plan.new_word_ids else []
        review_word_ids = json.loads(plan.review_word_ids) if plan.review_word_ids else []

        return {
            'today_learned': plan.learned_count,
            'today_total': len(new_word_ids),
            'today_reviewed': plan.reviewed_count,
            'review_total': len(review_word_ids),
            'is_all_completed': plan.is_completed
        }

    @staticmethod
    def get_word_for_recognition(word_id):
        """获取词汇用于手势识别"""
        word = Word.query.get(word_id)
        if not word:
            return None

        # 延迟导入，避免循环依赖
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app import get_predictor

        predictor, backend_map = get_predictor()
        if predictor and backend_map:
            vocabulary_index = backend_map.get(word.backend_id, word.id)
        else:
            vocabulary_index = word.id

        return {
            'word_id': word.id,
            'word': word.word,
            'vocabulary_index': vocabulary_index,
            'backend_id': word.backend_id,
            'category': word.category
        }

    @staticmethod
    def _get_next_valid_question(user_id, word_ids, session_type, max_stage, current_word_id=None, current_stage=None, answered_word_ids=None):
        """
        获取下一个有效题目
        规则：
        - 阶段优先遍历（先完成所有词的一个阶段，再进入下一个阶段）
        - 答错的题在当前词后续阶段完成后重新出现
        - answered_word_ids: 记录哪些词当前阶段已答对（用于标记哪些词可以进入下一阶段）
        """
        words = Word.query.filter(Word.id.in_(word_ids)).all()
        word_map = {w.id: w for w in words}

        # 获取所有进度记录
        progress_records = LearningProgress.query.filter(
            LearningProgress.user_id == user_id,
            LearningProgress.word_id.in_(word_ids),
            LearningProgress.session_type == session_type
        ).all()
        progress_map = {p.word_id: p for p in progress_records}

        # 如果没有传入 answered_word_ids，默认全部已答对（允许进入下一阶段）
        if answered_word_ids is None:
            answered_word_ids = set(word_ids)

        def is_stage_passed(progress, stage):
            """检查某阶段是否已通过"""
            if not progress:
                return False
            if stage == 1:
                return progress.stage1_passed
            elif stage == 2:
                return progress.stage2_passed
            elif stage == 3:
                return progress.stage3_passed
            elif stage == 4:
                return progress.stage4_passed
            return False

        def is_stage_skipped(progress, stage, session_type):
            """检查某阶段是否跳过"""
            if session_type == 'review' and stage == 1:
                return True
            if progress and stage == 1:
                return progress.stage1_skipped
            return False

        def can_advance_to_stage(progress, stage, session_type, answered_ids):
            """
            检查是否可以进入某阶段
            需要前置阶段全部完成，且该词在上一轮中已答对
            """
            if is_stage_skipped(progress, stage, session_type):
                return False
            if is_stage_passed(progress, stage):
                return False

            # 检查前置阶段
            for prev_stage in range(1, stage):
                if not is_stage_skipped(progress, prev_stage, session_type):
                    if not is_stage_passed(progress, prev_stage):
                        return False

            # 检查该词是否在上一轮中正确完成
            return progress is None or progress.word_id in answered_ids

        # 阶段优先遍历
        for stage in range(1, max_stage + 1):
            for word_id in word_ids:
                word = word_map.get(word_id)
                if not word:
                    continue

                progress = progress_map.get(word_id)

                # 跳过当前刚答错的词/阶段
                if word_id == current_word_id and stage == current_stage:
                    continue

                # 复习模式阶段1跳过
                if session_type == 'review' and stage == 1:
                    continue

                # 检查是否可以进入该阶段
                if not can_advance_to_stage(progress, stage, session_type, answered_word_ids):
                    continue

                # 构建题目
                item = {
                    'word_id': word_id,
                    'word': word.word,
                    'stage': stage,
                    'stage_name': STAGE_NAMES[stage],
                    'stage_description': STAGE_DESCRIPTIONS[stage],
                    'session_type': session_type
                }

                if stage == 1:
                    item['video_url'] = word.demo_video_url
                    item['image_url'] = word.image_url
                    item['steps'] = json.loads(word.steps) if word.steps else []
                    item['tips'] = json.loads(word.tips) if word.tips else []
                    item['category'] = word.category
                    item['difficulty'] = word.difficulty
                elif stage == 2:
                    choice_data = LearningCenterService._get_or_create_choice_options(
                        user_id, word_id, session_type, word
                    )
                    item['question_text'] = choice_data['question_text']
                    item['options'] = choice_data['options']
                    item['correct_index'] = choice_data['correct_index']
                elif stage == 3:
                    item['video_url'] = word.demo_video_url
                    item['image_url'] = word.image_url
                elif stage == 4:
                    item['target_word'] = word.word
                    item['category'] = word.category

                return item

        # 如果同阶段都处理完了，检查当前词是否可以进入下一阶段
        if current_word_id and current_stage:
            progress = progress_map.get(current_word_id)
            word = word_map.get(current_word_id)
            next_stage = current_stage + 1

            if word and next_stage <= max_stage:
                if can_advance_to_stage(progress, next_stage, session_type, set()):
                    # 答错的词重新进入下一阶段
                    item = {
                        'word_id': current_word_id,
                        'word': word.word,
                        'stage': next_stage,
                        'stage_name': STAGE_NAMES[next_stage],
                        'stage_description': STAGE_DESCRIPTIONS[next_stage],
                        'session_type': session_type,
                        'is_retry': True
                    }
                    if next_stage == 1:
                        item['video_url'] = word.demo_video_url
                        item['image_url'] = word.image_url
                        item['steps'] = json.loads(word.steps) if word.steps else []
                        item['tips'] = json.loads(word.tips) if word.tips else []
                        item['category'] = word.category
                        item['difficulty'] = word.difficulty
                    elif next_stage == 2:
                        choice_data = LearningCenterService._get_or_create_choice_options(
                            user_id, current_word_id, session_type, word
                        )
                        item['question_text'] = choice_data['question_text']
                        item['options'] = choice_data['options']
                        item['correct_index'] = choice_data['correct_index']
                    elif next_stage == 3:
                        item['video_url'] = word.demo_video_url
                        item['image_url'] = word.image_url
                    elif next_stage == 4:
                        item['target_word'] = word.word
                        item['category'] = word.category
                    return item

        return None  # 没有更多题目
