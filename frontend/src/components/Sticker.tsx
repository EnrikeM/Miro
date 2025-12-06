import React, { useEffect, useRef } from 'react';

import type { Sticker as StickerType } from '@/types';

interface StickerProps {
    data: StickerType;
    isSelected: boolean;
    onSelect: (id: string) => void;
    onUpdate: (id: string, updates: Partial<StickerType>) => void;
    onDelete: (id: string) => void;
    onMouseDown: (e: React.MouseEvent, id: string) => void;
    onResizeStart?: (e: React.MouseEvent, id: string, handle: string) => void;
    readOnly?: boolean;
}

export const Sticker: React.FC<StickerProps> = ({
    data,
    isSelected,
    onSelect,
    onUpdate,
    onDelete,
    onMouseDown,
    onResizeStart,
    readOnly,
}) => {
    const [isEditing, setIsEditing] = React.useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (isEditing && textareaRef.current) {
            textareaRef.current.focus();
            textareaRef.current.setSelectionRange(
                textareaRef.current.value.length,
                textareaRef.current.value.length,
            );
        }
    }, [isEditing]);

    const handleMouseDown = (e: React.MouseEvent) => {
        e.stopPropagation();
        onSelect(data.id);
        onMouseDown(e, data.id);
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!readOnly) setIsEditing(true);
    };

    const handleBlur = () => {
        setIsEditing(false);
    };

    const handleResizeDown = (e: React.MouseEvent, handle: string) => {
        e.stopPropagation();
        if (!readOnly) onResizeStart?.(e, data.id, handle);
    };

    return (
        <div
            className={`absolute shadow-lg transition-shadow group flex items-center justify-center ${isSelected ? 'ring-2 ring-purple-500 z-50 shadow-2xl' : 'hover:shadow-xl z-20'}`}
            style={{
                left: data.x,
                top: data.y,
                width: data.width,
                height: data.height,
                backgroundColor: data.color,
                transition: 'box-shadow 0.2s',
            }}
            onMouseDown={handleMouseDown}
            onDoubleClick={handleDoubleClick}
        >
            {isSelected && !isEditing && !readOnly && (
                <button
                    className="absolute -top-3 -right-3 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center shadow-md hover:bg-red-600 transition-colors z-[60] text-xs"
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete(data.id);
                    }}
                    onMouseDown={(e) => e.stopPropagation()}
                >
                    ✕
                </button>
            )}

            {isSelected && !isEditing && onResizeStart && !readOnly && (
                <>
                    <div
                        className="absolute -top-1 -left-1 w-3 h-3 bg-white border border-purple-500 rounded-full cursor-nwse-resize z-[60]"
                        onMouseDown={(e) => handleResizeDown(e, 'tl')}
                    />
                    <div
                        className="absolute -bottom-1 -left-1 w-3 h-3 bg-white border border-purple-500 rounded-full cursor-nesw-resize z-[60]"
                        onMouseDown={(e) => handleResizeDown(e, 'bl')}
                    />
                    <div
                        className="absolute -bottom-1 -right-1 w-3 h-3 bg-white border border-purple-500 rounded-full cursor-nwse-resize z-[60]"
                        onMouseDown={(e) => handleResizeDown(e, 'br')}
                    />
                </>
            )}

            {isEditing ? (
                <textarea
                    ref={textareaRef}
                    className="w-full h-full bg-transparent outline-none p-4 text-center resize-none flex items-center justify-center content-center font-medium text-gray-800 leading-normal placeholder-gray-500/50"
                    style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                    value={data.text}
                    onChange={(e) => {
                        if (!readOnly) onUpdate(data.id, { text: e.target.value });
                    }}
                    onBlur={handleBlur}
                    onKeyDown={(e) => e.stopPropagation()}
                    placeholder="Введите текст..."
                />
            ) : (
                <div className="w-full h-full p-4 flex items-center justify-center text-center font-medium text-gray-800 overflow-hidden pointer-events-none select-none break-words whitespace-pre-wrap">
                    {data.text || <span className="opacity-0">Empty</span>}
                </div>
            )}
        </div>
    );
};
