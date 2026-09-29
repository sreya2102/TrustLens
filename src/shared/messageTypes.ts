import { ExtractedData, ScanResult } from './types';

export type MessageType = 'SCAN_PAGE' | 'SCAN_RESULTS';

export interface ScanPageMessage {
  type: 'SCAN_PAGE';
}

export interface ScanResultsMessage {
  type: 'SCAN_RESULTS';
  data: ScanResult;
}

export type ExtensionMessage = ScanPageMessage | ScanResultsMessage;

export type { ExtractedData };
