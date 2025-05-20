
declare module '@/components/ui/tooltip' {
  export interface TooltipProps {
    tooltip: string;
    children: React.ReactNode;
  }
  
  export const Tooltip: React.FC<TooltipProps>;
}