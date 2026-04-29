# Material Slot Cleanup for Blender

Blender add-on for cleaning material slots and unused data.

面板位置：Material Properties > Material Slot Cleanup，會顯示在 Preview / Surface 面板上方。

## 功能說明

1. 移除未被面使用的材質槽
2. 移除空的材質槽
3. 清掉 Blender 裡沒有使用者的 orphan data

執行時會處理目前選取的 Mesh 物件，並在清理後還原原本的選取狀態。

如果物件的面目前只指到空白材質槽，script 會保留第一個非空材質並讓面改用它，避免清理後物件沒有任何材質。

## 使用方式

1. 在 Blender 安裝並啟用 `material_slot_cleanup_for_blender.py`
2. 選取要清理的 Mesh 物件
3. 到 Material Properties 開啟 Material Slot Cleanup 面板
4. 視需求勾選 Purge Orphan Data
5. 按下 Clean Material Slots
