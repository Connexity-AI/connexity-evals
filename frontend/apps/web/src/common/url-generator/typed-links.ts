import type { Route } from 'next';
import {
  createSerializer,
  type CreateSerializerOptions,
  type inferParserType,
  type Nullable,
  type ParserMap,
} from 'nuqs/server';

export function createTypedLink<Parsers extends ParserMap>(
  route: Route,
  parsers: Parsers,
  options: CreateSerializerOptions<Parsers> = {},
) {
  const serialize = createSerializer<Parsers, Route, Route>(parsers, options);
  return (values: Partial<Nullable<inferParserType<Parsers>>> = {}) =>
    serialize(route, values);
}
