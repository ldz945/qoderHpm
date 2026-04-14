<template>
  <div class="document-tree">
    <a-card title="文档管理" :bordered="false">
      <a-row :gutter="24">
        <!-- 左侧目录树 -->
        <a-col :span="8">
          <a-card title="文档目录" size="small">
            <template #extra>
              <a-button type="primary" size="small" @click="handleAddRootFolder">
                <template #icon><PlusOutlined /></template>
                新建根目录
              </a-button>
            </template>
            <a-tree
              :tree-data="treeData"
              :selected-keys="selectedKeys"
              :expanded-keys="expandedKeys"
              @select="handleTreeSelect"
              @expand="handleTreeExpand"
              @right-click="handleTreeRightClick"
            >
              <template #title="{ title, key }">
                <span>{{ title }}</span>
              </template>
            </a-tree>
          </a-card>
        </a-col>

        <!-- 右侧文件列表 -->
        <a-col :span="16">
          <a-card :title="currentFolderName" size="small">
            <template #extra>
              <a-upload
                :action="uploadAction"
                :headers="uploadHeaders"
                :data="{ folder: selectedFolderId }"
                @change="handleUploadChange"
                :disabled="!selectedFolderId"
              >
                <a-button type="primary" :disabled="!selectedFolderId">
                  <template #icon><UploadOutlined /></template>
                  上传文件
                </a-button>
              </a-upload>
            </template>

            <a-table
              :columns="columns"
              :data-source="fileList"
              :loading="loading"
              :pagination="pagination"
              row-key="id"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'fileName'">
                  <FileOutlined />
                  <span style="margin-left: 8px">{{ record.fileName }}</span>
                </template>
                <template v-if="column.key === 'isLatest'">
                  <a-tag :color="record.isLatest ? 'success' : 'default'">
                    {{ record.isLatest ? '最新' : '旧版本' }}
                  </a-tag>
                </template>
                <template v-if="column.key === 'fileSize'">
                  {{ formatFileSize(record.fileSize) }}
                </template>
                <template v-if="column.key === 'action'">
                  <a-button type="link" @click="handleDownload(record)">下载</a-button>
                  <a-button type="link" @click="handleViewHistory(record)">历史版本</a-button>
                  <a-button type="link" danger @click="handleDeleteFile(record)">删除</a-button>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </a-card>

    <!-- 右键菜单 -->
    <a-menu
      v-if="contextMenuVisible"
      :style="{ position: 'fixed', left: `${contextMenuX}px`, top: `${contextMenuY}px`, zIndex: 1000 }"
      @click="handleContextMenuClick"
    >
      <a-menu-item key="addChild">新建子文件夹</a-menu-item>
      <a-menu-item key="edit">编辑</a-menu-item>
      <a-menu-item key="delete" danger>删除</a-menu-item>
    </a-menu>

    <!-- 新建/编辑文件夹弹窗 -->
    <a-modal
      v-model:open="folderModalVisible"
      :title="folderModalTitle"
      @ok="handleFolderModalOk"
      @cancel="handleFolderModalCancel"
    >
      <a-form :model="folderForm" layout="vertical">
        <a-form-item label="文件夹名称" required>
          <a-input v-model:value="folderForm.name" placeholder="请输入文件夹名称" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 历史版本弹窗 -->
    <a-modal
      v-model:open="historyModalVisible"
      title="历史版本"
      width="800px"
      :footer="null"
    >
      <a-table
        :columns="historyColumns"
        :data-source="historyList"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-button type="link" @click="handleDownload(record)">下载</a-button>
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, UploadOutlined, FileOutlined, FolderOutlined } from '@ant-design/icons-vue'
import { getDocuments, createDocument, updateDocument, deleteDocument } from '@/api/auxiliary'
import { getDocumentFiles, deleteDocumentFile } from '@/api/auxiliary'

// 树形数据
const treeData = ref([])
const selectedKeys = ref([])
const expandedKeys = ref([])
const selectedFolderId = ref(null)
const currentFolderName = computed(() => {
  if (!selectedFolderId.value) return '请选择文件夹'
  return findFolderName(treeData.value, selectedFolderId.value) || '文件列表'
})

// 文件列表
const fileList = ref([])
const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuNode = ref(null)

// 文件夹弹窗
const folderModalVisible = ref(false)
const folderModalTitle = ref('')
const folderForm = reactive({
  id: null,
  name: '',
  parent: null
})
const isEditFolder = ref(false)

// 历史版本弹窗
const historyModalVisible = ref(false)
const historyList = ref([])

// 表格列定义
const columns = [
  {
    title: '文件名',
    dataIndex: 'fileName',
    key: 'fileName',
    ellipsis: true
  },
  {
    title: '版本号',
    dataIndex: 'version',
    key: 'version',
    width: 80
  },
  {
    title: '文件大小',
    dataIndex: 'fileSize',
    key: 'fileSize',
    width: 100
  },
  {
    title: '上传人',
    dataIndex: 'uploadByName',
    key: 'uploadByName',
    width: 100
  },
  {
    title: '上传时间',
    dataIndex: 'uploadTime',
    key: 'uploadTime',
    width: 160
  },
  {
    title: '是否最新',
    dataIndex: 'isLatest',
    key: 'isLatest',
    width: 90
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right'
  }
]

// 历史版本列定义
const historyColumns = [
  {
    title: '版本号',
    dataIndex: 'version',
    key: 'version',
    width: 80
  },
  {
    title: '文件名',
    dataIndex: 'fileName',
    key: 'fileName'
  },
  {
    title: '文件大小',
    dataIndex: 'fileSize',
    key: 'fileSize',
    width: 100
  },
  {
    title: '上传人',
    dataIndex: 'uploadByName',
    key: 'uploadByName',
    width: 100
  },
  {
    title: '上传时间',
    dataIndex: 'uploadTime',
    key: 'uploadTime',
    width: 160
  },
  {
    title: '操作',
    key: 'action',
    width: 80
  }
]

// 上传配置
const uploadAction = '/api/auxiliary/document-files/upload/'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}

// 查找文件夹名称
const findFolderName = (tree, id) => {
  for (const node of tree) {
    if (node.key === id) return node.title
    if (node.children) {
      const name = findFolderName(node.children, id)
      if (name) return name
    }
  }
  return null
}

// 加载目录树
const loadTreeData = async () => {
  try {
    const res = await getDocuments({ page_size: 9999 })
    const docs = res.results || []
    treeData.value = buildTree(docs)
  } catch (error) {
    message.error('加载目录失败')
  }
}

// 构建树形结构
const buildTree = (docs) => {
  const map = {}
  const roots = []
  
  docs.forEach(doc => {
    map[doc.id] = {
      title: doc.name,
      key: doc.id,
      children: [],
      ...doc
    }
  })
  
  docs.forEach(doc => {
    if (doc.parent && map[doc.parent]) {
      map[doc.parent].children.push(map[doc.id])
    } else {
      roots.push(map[doc.id])
    }
  })
  
  return roots
}

// 加载文件列表
const loadFileList = async () => {
  if (!selectedFolderId.value) {
    fileList.value = []
    return
  }
  loading.value = true
  try {
    const res = await getDocumentFiles({
      folder: selectedFolderId.value,
      page: pagination.current,
      page_size: pagination.pageSize
    })
    fileList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    message.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// 树节点选择
const handleTreeSelect = (keys, info) => {
  selectedKeys.value = keys
  selectedFolderId.value = keys[0] || null
  loadFileList()
}

// 树节点展开
const handleTreeExpand = (keys) => {
  expandedKeys.value = keys
}

// 树节点右键
const handleTreeRightClick = ({ event, node }) => {
  event.preventDefault()
  contextMenuVisible.value = true
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuNode.value = node
}

// 右键菜单点击
const handleContextMenuClick = ({ key }) => {
  contextMenuVisible.value = false
  const node = contextMenuNode.value
  
  if (key === 'addChild') {
    isEditFolder.value = false
    folderForm.id = null
    folderForm.name = ''
    folderForm.parent = node.key
    folderModalTitle.value = '新建子文件夹'
    folderModalVisible.value = true
  } else if (key === 'edit') {
    isEditFolder.value = true
    folderForm.id = node.key
    folderForm.name = node.title
    folderForm.parent = node.parent || null
    folderModalTitle.value = '编辑文件夹'
    folderModalVisible.value = true
  } else if (key === 'delete') {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件夹 "${node.title}" 吗？`,
      onOk: async () => {
        try {
          await deleteDocument(node.key)
          message.success('删除成功')
          loadTreeData()
        } catch (error) {
          message.error('删除失败')
        }
      }
    })
  }
}

// 新建根目录
const handleAddRootFolder = () => {
  isEditFolder.value = false
  folderForm.id = null
  folderForm.name = ''
  folderForm.parent = null
  folderModalTitle.value = '新建根目录'
  folderModalVisible.value = true
}

// 文件夹弹窗确认
const handleFolderModalOk = async () => {
  if (!folderForm.name.trim()) {
    message.error('请输入文件夹名称')
    return
  }
  
  try {
    if (isEditFolder.value) {
      await updateDocument(folderForm.id, { name: folderForm.name })
    } else {
      await createDocument({
        name: folderForm.name,
        parent: folderForm.parent
      })
    }
    message.success(isEditFolder.value ? '更新成功' : '创建成功')
    folderModalVisible.value = false
    loadTreeData()
  } catch (error) {
    message.error(isEditFolder.value ? '更新失败' : '创建失败')
  }
}

// 文件夹弹窗取消
const handleFolderModalCancel = () => {
  folderModalVisible.value = false
}

// 上传变化
const handleUploadChange = (info) => {
  if (info.file.status === 'done') {
    message.success(`${info.file.name} 上传成功`)
    loadFileList()
  } else if (info.file.status === 'error') {
    message.error(`${info.file.name} 上传失败`)
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (!size) return '-'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

// 下载文件
const handleDownload = (record) => {
  window.open(`/api/auxiliary/document-files/${record.id}/download/`)
}

// 查看历史版本
const handleViewHistory = async (record) => {
  try {
    const res = await getDocumentFiles({
      file_name: record.fileName,
      page_size: 9999
    })
    historyList.value = res.results || []
    historyModalVisible.value = true
  } catch (error) {
    message.error('加载历史版本失败')
  }
}

// 删除文件
const handleDeleteFile = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除文件 "${record.fileName}" 吗？`,
    onOk: async () => {
      try {
        await deleteDocumentFile(record.id)
        message.success('删除成功')
        loadFileList()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

// 点击外部关闭右键菜单
const handleClickOutside = () => {
  contextMenuVisible.value = false
}

onMounted(() => {
  loadTreeData()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.document-tree {
  padding: 24px;
}
</style>
