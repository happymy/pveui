from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils.module_loading import import_string
from django.utils import timezone
import logging

from apps.tasks.models import Job

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))
    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()


def _parse_cron_expression(cron_expr: str):
    """解析cron表达式为CronTrigger参数
    
    支持格式：
    - 5位: 分 时 日 月 周 (标准cron)
    - 6位: 秒 分 时 日 月 周 (APScheduler格式)
    """
    parts = cron_expr.strip().split()
    if len(parts) == 5:
        # 标准5位，补充秒位为0
        minute, hour, day, month, day_of_week = parts
        return {
            'second': '0',
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week,
        }
    elif len(parts) == 6:
        # 6位格式
        second, minute, hour, day, month, day_of_week = parts
        return {
            'second': second,
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week,
        }
    else:
        raise ValueError(f'无效的cron表达式: {cron_expr}，应为5位或6位')


def _build_trigger(job: Job):
    """从job构建CronTrigger"""
    cron_params = _parse_cron_expression(job.cron_expression)
    return CronTrigger(**cron_params)


def _import_func(func_name: str):
    """导入任务函数
    
    支持格式：
    - 函数名（从 apps.tasks.task 模块导入）: NoParams, Params, reset_admin_password
    - 完整路径（模块路径:函数名）: apps.pve.tasks:create_vm_backup, apps.pve.tasks:create_vm_snapshot
    """
    # 如果包含冒号，说明是完整路径格式
    if ':' in func_name:
        try:
            return import_string(func_name)
        except ImportError as e:
            raise ImportError(f'无法导入任务函数 {func_name}: {e}')
        except Exception as e:
            raise ImportError(f'导入任务函数 {func_name} 时出错: {e}')
    
    # 否则尝试从 apps.tasks.task 模块导入
    try:
        from apps.tasks import task
        if hasattr(task, func_name):
            return getattr(task, func_name)
    except Exception:
        pass
    
    # 如果还是找不到，尝试完整路径导入（向后兼容）
    try:
        return import_string(f'apps.tasks.task:{func_name}')
    except Exception:
        raise ImportError(f'无法导入任务函数: {func_name}。请使用完整路径格式，如: apps.pve.tasks:create_vm_backup')


def add_or_update_job(job: Job) -> None:
    """添加或更新任务到调度器"""
    scheduler = get_scheduler()
    if not job.enabled:
        remove_job(job)
        return
    
    try:
        trigger = _build_trigger(job)
        func = _import_func(job.invoke_target)
        job_id = job.job_id or f'task-{job.pk}'
        
        # 移除已存在的任务
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass
        
        # 添加任务
        scheduler_job = scheduler.add_job(
            func=func,
            trigger=trigger,
            args=job.job_params or [],
            id=job_id,
            replace_existing=True,
        )
        
        # 更新job_id和下次执行时间
        next_run = scheduler_job.next_run_time
        Job.objects.filter(pk=job.pk).update(
            job_id=job_id,
            next_valid_time=next_run
        )
        logger.info(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 已添加到调度器，下次执行时间: {next_run}')
    except ValueError as e:
        logger.error(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 添加失败: Cron表达式错误 - {e}')
        raise
    except ImportError as e:
        logger.error(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 添加失败: 无法导入函数 "{job.invoke_target}" - {e}')
        raise
    except Exception as e:
        logger.exception(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 添加失败: {e}')
        raise


def remove_job(job: Job) -> None:
    """从调度器移除任务"""
    if not job.job_id:
        return
    try:
        get_scheduler().remove_job(job.job_id)
    except Exception:
        pass


def sync_all_jobs_from_db() -> None:
    """从数据库同步所有启用的任务到调度器"""
    jobs = Job.objects.filter(status=1)
    logger.info(f'[定时任务] 开始同步 {jobs.count()} 个启用的任务到调度器')
    success_count = 0
    fail_count = 0
    
    for job in jobs:
        try:
            add_or_update_job(job)
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f'[定时任务] 同步任务 "{job.job_name}" (ID: {job.pk}) 失败: {e}')
            # 跳过有问题的任务，继续处理其他任务
            continue
    
    logger.info(f'[定时任务] 任务同步完成: 成功 {success_count} 个, 失败 {fail_count} 个')


def run_job_now(job: Job) -> None:
    """立即执行任务"""
    try:
        func = _import_func(job.invoke_target)
        logger.info(f'[定时任务] 立即执行任务 "{job.job_name}" (ID: {job.pk}), 调用目标: {job.invoke_target}, 参数: {job.job_params}')
        func(*(job.job_params or []))
        Job.objects.filter(pk=job.pk).update(last_run_at=timezone.now())
        logger.info(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 执行完成')
    except ImportError as e:
        logger.error(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 执行失败: 无法导入函数 "{job.invoke_target}" - {e}')
        raise
    except Exception as e:
        logger.exception(f'[定时任务] 任务 "{job.job_name}" (ID: {job.pk}) 执行失败: {e}')
        raise
