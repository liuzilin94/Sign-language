"""
学习中心API路由
"""
import os
import tempfile
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np

from backend.models import db, Word, DailyPlan
from backend.learning_service import LearningCenterService

# 创建蓝图
learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')


def success_response(data=None, message="success", code=200):
    """成功响应"""
    return jsonify({'code': code, 'message': message, 'data': data, 'timestamp': datetime.now().timestamp()})


def error_response(message, code=400, error_code=None):
    """错误响应"""
    return jsonify({
        'code': error_code or code,
        'message': message,
        'data': None,
        'timestamp': datetime.now().timestamp()
    }), code


@learning_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """获取学习设置"""
    try:
        user_id = int(get_jwt_identity())
        settings = LearningCenterService.get_or_create_settings(user_id)
        return success_response(settings.to_dict())
    except Exception as e:
        return error_response(f"获取设置失败: {str(e)}", 500)


@learning_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """更新学习设置"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        daily_new_words = data.get('daily_new_words')
        daily_review_words = data.get('daily_review_words')

        settings = LearningCenterService.update_settings(user_id, daily_new_words, daily_review_words)
        return success_response(settings, "设置已更新")
    except Exception as e:
        return error_response(f"更新设置失败: {str(e)}", 500)


@learning_bp.route('/today-plan', methods=['GET'])
@jwt_required()
def get_today_plan():
    """获取今日学习计划"""
    try:
        user_id = int(get_jwt_identity())
        plan_data = LearningCenterService.get_today_plan(user_id)
        return success_response(plan_data)
    except Exception as e:
        return error_response(f"获取计划失败: {str(e)}", 500)


@learning_bp.route('/today-plan/reset', methods=['POST'])
@jwt_required()
def reset_today_plan():
    """重置今日学习计划（用于设置变更后重新生成）"""
    try:
        user_id = int(get_jwt_identity())
        today = date.today()

        # 删除今日计划
        plan = DailyPlan.query.filter_by(user_id=user_id, plan_date=today).first()
        if plan:
            db.session.delete(plan)
            db.session.commit()

        return success_response({"message": "今日计划已重置，重新进入学习页面将生成新计划"})
    except Exception as e:
        return error_response(f"重置计划失败: {str(e)}", 500)


@learning_bp.route('/start-session', methods=['POST'])
@jwt_required()
def start_session():
    """开始学习/复习会话"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        session_type = data.get('session_type', 'learn')

        if session_type not in ['learn', 'review']:
            return error_response("session_type必须是learn或review", 400)

        result, error = LearningCenterService.start_session(user_id, session_type)
        if error:
            return error_response(error, 400)

        return success_response(result)
    except Exception as e:
        return error_response(f"启动会话失败: {str(e)}", 500)


@learning_bp.route('/submit-answer', methods=['POST'])
@jwt_required()
def submit_answer():
    """提交答案"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        word_id = data.get('word_id')
        session_type = data.get('session_type', 'learn')
        stage = data.get('stage')
        answer_data = data.get('answer', {})

        if not word_id or not stage:
            return error_response("word_id和stage不能为空", 400)

        result = LearningCenterService.submit_answer(
            user_id, word_id, session_type, stage, answer_data
        )
        return success_response(result)
    except Exception as e:
        return error_response(f"提交答案失败: {str(e)}", 500)


@learning_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """获取学习进度"""
    try:
        user_id = int(get_jwt_identity())
        summary = LearningCenterService.get_progress_summary(user_id)
        return success_response(summary)
    except Exception as e:
        return error_response(f"获取进度失败: {str(e)}", 500)


@learning_bp.route('/recognition-info/<int:word_id>', methods=['GET'])
@jwt_required()
def get_recognition_info(word_id):
    """获取词汇识别信息"""
    try:
        info = LearningCenterService.get_word_for_recognition(word_id)
        if not info:
            return error_response("词汇不存在", 404)
        return success_response(info)
    except Exception as e:
        return error_response(f"获取识别信息失败: {str(e)}", 500)
