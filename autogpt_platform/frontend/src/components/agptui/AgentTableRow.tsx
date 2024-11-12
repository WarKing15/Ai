import * as React from "react";
import Image from "next/image";
import { Button } from "./Button";
import { IconStarFilled, IconEdit, IconMore } from "@/components/ui/icons";
import { Status, StatusType } from "./Status";

export interface AgentTableRowProps {
  agentName: string;
  description: string;
  imageSrc: string;
  dateSubmitted: string;
  status: StatusType;
  runs?: number;
  rating?: number;
  onEdit: () => void;
  id: string;
}

export const AgentTableRow: React.FC<AgentTableRowProps> = ({
  agentName,
  description,
  imageSrc,
  dateSubmitted,
  status,
  runs,
  rating,
  onEdit,
  id,
}) => {
  // Create a unique ID for the checkbox
  const checkboxId = `agent-${id}-checkbox`;

  return (
    <div className="hidden md:flex items-center px-4 py-4 border-b border-neutral-300 hover:bg-neutral-50">
      <div className="flex items-center">
        <div className="flex items-center">
          <input 
            type="checkbox" 
            id={checkboxId}
            aria-label={`Select ${agentName}`}
            className="w-5 h-5 rounded border-2 border-neutral-400 mr-4" 
          />
          {/* Single label instead of multiple */}
          <label 
            htmlFor={checkboxId}
            className="sr-only"
          >
            Select {agentName}
          </label>
        </div>
      </div>
      
      <div className="grid grid-cols-[minmax(400px,1fr),180px,140px,100px,100px,40px] gap-4 w-full items-center">
        {/* Agent info column */}
        <div className="flex items-center gap-4">
          <div className="relative w-[125px] h-[70px] overflow-hidden rounded-[10px] bg-[#d9d9d9]">
            <Image
              src={imageSrc}
              alt={agentName}
              layout="fill"
              objectFit="cover"
            />
          </div>
          <div className="flex flex-col">
            <h3 className="text-[15px] font-medium text-neutral-800">
              {agentName}
            </h3>
            <p className="text-sm text-neutral-600 line-clamp-2">
              {description}
            </p>
          </div>
        </div>

        {/* Date column */}
        <div className="text-sm text-neutral-600 pl-14">
          {dateSubmitted}
        </div>

        {/* Status column */}
        <div>
          <Status status={status} />
        </div>

        {/* Runs column */}
        <div className="text-sm text-neutral-600 text-right">
          {runs?.toLocaleString() ?? '—'}
        </div>

        {/* Reviews column */}
        <div className="text-right">
          {rating ? (
            <div className="flex items-center justify-end gap-1">
              <span className="text-sm font-medium text-neutral-800">
                {rating.toFixed(1)}
              </span>
              <IconStarFilled className="h-4 w-4 text-neutral-800" />
            </div>
          ) : (
            <span className="text-sm text-neutral-600">—</span>
          )}
        </div>

        {/* Actions - Three dots menu */}
        <div className="flex justify-end">
          <button
            onClick={onEdit}
            className="p-1 hover:bg-neutral-100 rounded-full"
          >
            <IconMore className="h-5 w-5 text-neutral-800" />
          </button>
        </div>
      </div>
    </div>
  );
};
