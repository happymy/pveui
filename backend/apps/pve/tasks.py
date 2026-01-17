"""PVE 虚拟机定时任务函数"""
import logging
from typing import Dict, Any
from django.utils import timezone

from apps.pve.models import VirtualMachine
from apps.pve.pve_client import PVEAPIClient

logger = logging.getLogger(__name__)


def create_vm_backup(vm_id: int, storage: str = None, mode: str = 'snapshot', 
                     compress: str = 'zstd', remove: bool = False, notes: str = ''):
    """
    创建虚拟机备份定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
        storage: 存储名称（可选，如果不提供则使用默认存储）
        mode: 备份模式，默认 'snapshot'
        compress: 压缩格式，默认 'zstd'
        remove: 是否删除旧备份，默认 False
        notes: 备份备注
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 如果没有指定存储，尝试获取第一个可用存储
        if not storage:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            # 获取节点存储列表
            storages = client.get_storage(vm.node)
            # 查找支持备份的存储
            backup_storage = None
            for st in storages:
                if st.get('content') and 'backup' in st.get('content', []):
                    backup_storage = st.get('storage')
                    break
            
            if not backup_storage:
                logger.error(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 备份失败: 未找到可用的备份存储')
                return
            
            storage = backup_storage
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 创建备份
        result = client.create_backup(
            node=vm.node,
            vmid=vm.vmid,
            storage=storage,
            mode=mode,
            compress=compress,
            remove=remove,
            notes=notes or f'定时备份-{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 备份任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机备份失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机备份失败: {e}')


def create_vm_snapshot(vm_id: int, name: str = None, description: str = '', 
                      include_memory: bool = False):
    """
    创建虚拟机快照定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
        name: 快照名称（可选，如果不提供则自动生成）
        description: 快照描述
        include_memory: 是否包含内存，默认 False
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 如果没有指定快照名称，自动生成
        if not name:
            name = f'snapshot-{timezone.now().strftime("%Y%m%d-%H%M%S")}'
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 创建快照
        result = client.create_snapshot(
            node=vm.node,
            vmid=vm.vmid,
            name=name,
            description=description or f'定时快照-{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
            include_memory=include_memory
        )
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 快照任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机快照失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机快照失败: {e}')


def start_vm(vm_id: int):
    """
    启动虚拟机定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 启动虚拟机
        result = client.start_vm(node=vm.node, vmid=vm.vmid)
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 启动任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机启动失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机启动失败: {e}')


def stop_vm(vm_id: int):
    """
    停止虚拟机定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 停止虚拟机
        result = client.stop_vm(node=vm.node, vmid=vm.vmid)
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 停止任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机停止失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机停止失败: {e}')


def shutdown_vm(vm_id: int):
    """
    关闭虚拟机定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 关闭虚拟机
        result = client.shutdown_vm(node=vm.node, vmid=vm.vmid)
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 关闭任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机关闭失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机关闭失败: {e}')


def reboot_vm(vm_id: int):
    """
    重启虚拟机定时任务
    
    参数:
        vm_id: 虚拟机ID（数据库主键）
    """
    try:
        vm = VirtualMachine.objects.get(pk=vm_id)
        server = vm.server
        
        # 创建 PVE 客户端
        client = PVEAPIClient(
            host=server.host,
            port=server.port,
            token_id=server.token_id,
            token_secret=server.token_secret,
            verify_ssl=server.verify_ssl
        )
        
        # 重启虚拟机
        result = client.reboot_vm(node=vm.node, vmid=vm.vmid)
        
        logger.info(f'[定时任务] 虚拟机 {vm.name}({vm.vmid}) 重启任务已创建: {result}')
        return result
        
    except VirtualMachine.DoesNotExist:
        logger.error(f'[定时任务] 虚拟机重启失败: 虚拟机ID {vm_id} 不存在')
    except Exception as e:
        logger.exception(f'[定时任务] 虚拟机重启失败: {e}')
