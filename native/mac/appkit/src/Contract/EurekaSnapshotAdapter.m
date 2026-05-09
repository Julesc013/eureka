#import "EurekaSnapshotAdapter.h"

@implementation EurekaSnapshotAdapter

+ (BOOL)textLooksLikeSnapshot:(NSString *)text
{
    if (text == nil) {
        return NO;
    }
    if ([text rangeOfString:@"snapshot_manifest"].location != NSNotFound) {
        return YES;
    }
    return [text rangeOfString:@"snapshot_record"].location != NSNotFound;
}

+ (NSString *)fixtureSummary
{
    return @"Snapshot: local manifest and record fixture text only.";
}

@end
