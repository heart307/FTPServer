from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from app import db
from app.models import User, OperationLog
from app.api import api_bp
import re

class LoginSchema(Schema):
    """登录验证模式"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class RegisterSchema(Schema):
    """注册验证模式"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True)
    
    def validate_username(self, value):
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('用户名只能包含字母、数字和下划线')
        
        if User.query.filter_by(username=value).first():
            raise ValidationError('用户名已存在')
    
    def validate_email(self, value):
        """验证邮箱是否已存在"""
        if User.query.filter_by(email=value).first():
            raise ValidationError('邮箱已被注册')

class ChangePasswordSchema(Schema):
    """修改密码验证模式"""
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True)

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'message': '账户已被禁用'
                }), 403
            
            # 创建JWT令牌
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            # 更新最后登录信息
            user.update_last_login(request.remote_addr)
            
            # 记录登录日志
            OperationLog.log_success(
                user_id=user.id,
                operation='login',
                message='用户登录成功',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })
        else:
            # 记录登录失败日志
            OperationLog.log_failure(
                user_id=user.id if user else None,
                operation='login',
                message=f'用户 {data["username"]} 登录失败',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': '输入数据无效',
            'errors': e.messages
        }), 400
    except Exception as e:
        current_app.logger.error(f'登录错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        # 检查是否允许注册
        from app.models import SystemConfig
        if not SystemConfig.get_config('system.enable_registration', True):
            return jsonify({
                'success': False,
                'message': '系统暂不开放注册'
            }), 403
        
        schema = RegisterSchema()
        data = schema.load(request.get_json())
        
        # 验证密码确认
        if data['password'] != data['confirm_password']:
            return jsonify({
                'success': False,
                'message': '两次输入的密码不一致'
            }), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 记录注册日志
        OperationLog.log_success(
            user_id=user.id,
            operation='register',
            message='用户注册成功',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': '输入数据无效',
            'errors': e.messages
        }), 400
    except Exception as e:
        current_app.logger.error(f'注册错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '注册失败，请稍后重试'
        }), 500

@api_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': '用户不存在或已被禁用'
            }), 401
        
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'access_token': new_token
        })
        
    except Exception as e:
        current_app.logger.error(f'刷新令牌错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '刷新令牌失败'
        }), 500

@api_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict(include_sensitive=True)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取用户信息错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '获取用户信息失败'
        }), 500

@api_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新邮箱
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'success': False,
                    'message': '邮箱已被其他用户使用'
                }), 400
            user.email = data['email']
        
        db.session.commit()
        
        # 记录更新日志
        OperationLog.log_success(
            user_id=user.id,
            operation='update_profile',
            message='用户更新个人信息',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': '个人信息更新成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f'更新用户信息错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '更新用户信息失败'
        }), 500

@api_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json())
        
        # 验证旧密码
        if not user.check_password(data['old_password']):
            return jsonify({
                'success': False,
                'message': '原密码错误'
            }), 400
        
        # 验证新密码确认
        if data['new_password'] != data['confirm_password']:
            return jsonify({
                'success': False,
                'message': '两次输入的新密码不一致'
            }), 400
        
        # 更新密码
        user.set_password(data['new_password'])
        db.session.commit()
        
        # 记录密码修改日志
        OperationLog.log_success(
            user_id=user.id,
            operation='change_password',
            message='用户修改密码',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': '输入数据无效',
            'errors': e.messages
        }), 400
    except Exception as e:
        current_app.logger.error(f'修改密码错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '修改密码失败'
        }), 500

@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        current_user_id = get_jwt_identity()
        
        # 记录登出日志
        OperationLog.log_success(
            user_id=current_user_id,
            operation='logout',
            message='用户登出',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
        
    except Exception as e:
        current_app.logger.error(f'登出错误: {str(e)}')
        return jsonify({
            'success': False,
            'message': '登出失败'
        }), 500
