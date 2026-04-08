import { emptyParser, newAgentParser } from '@/common/url-generator/parsers';
import {
  type CreateSerializerOptions,
  type inferParserType,
  type Nullable,
  type ParserMap,
} from 'nuqs/server';

export type TypedLinkProps<Parsers extends ParserMap> = {
  options?: CreateSerializerOptions<Parsers>;
  values?: Partial<Nullable<inferParserType<Parsers>>>;
};

export type BaseRouteType = TypedLinkProps<typeof emptyParser>;

// ── Auth ──
export type AuthType = BaseRouteType;

// ── Dashboard ──
export type DashboardType = BaseRouteType;
export type AgentsType = BaseRouteType;
export type NewAgentType = TypedLinkProps<typeof newAgentParser>;
export type MetricsType = BaseRouteType;
export type SettingsType = BaseRouteType;
